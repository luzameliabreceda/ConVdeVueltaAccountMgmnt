from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status, Query, HTTPException
from injector import inject
from datetime import datetime, date
import uuid

from ..repositories.user_repository import UserRepository
from ..models.user import User


class TestRepositoryController:
    
    @inject
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        
        @self.router.post(
            "/test/create-sample-users",
            summary="Create Sample Users",
            description="Create multiple sample users for testing"
        )
        async def create_sample_users():
            """Create sample users for testing repository methods"""
            users_data = [
                {
                    "email": f"user{i}@test.com",
                    "username": f"user{i}",
                    "first_name": f"User{i}",
                    "paternal_surname": "TestSurname",
                    "maternal_surname": "TestMaternal",
                    "phone": f"555-000{i}",
                    "date_of_birth": date(1990 + i, 1, 15),
                    "gender": "M" if i % 2 == 0 else "F",
                    "national_id": f"123456789012{i}",
                    "enabled": i % 3 != 0  # Some disabled for testing
                }
                for i in range(1, 6)
            ]
            
            created_users = []
            for user_data in users_data:
                try:
                    # Check if user already exists
                    if not await self._user_repository.exists_by_email(user_data["email"]):
                        user = User(**user_data)
                        saved_user = await self._user_repository.save(user)
                        created_users.append(saved_user.to_dict())
                except Exception as e:
                    # Skip if user already exists
                    pass
            
            return {
                "message": f"Created {len(created_users)} sample users",
                "users": created_users
            }
        
        @self.router.get(
            "/test/save-all",
            summary="Test save_all method",
            description="Test the save_all batch method"
        )
        async def test_save_all():
            """Test save_all method with multiple users"""
            users = [
                User(
                    email=f"batch{i}@test.com",
                    username=f"batch{i}",
                    first_name=f"Batch{i}",
                    enabled=True
                )
                for i in range(1, 4)
            ]
            
            # Filter out existing users
            new_users = []
            for user in users:
                if not await self._user_repository.exists_by_email(user.email):
                    new_users.append(user)
            
            if new_users:
                saved_users = await self._user_repository.save_all(new_users)
                return {
                    "message": f"Saved {len(saved_users)} users in batch",
                    "users": [u.to_dict() for u in saved_users]
                }
            else:
                return {"message": "No new users to save"}
        
        @self.router.get(
            "/test/find-by",
            summary="Test find_by method",
            description="Test find_by with different conditions"
        )
        async def test_find_by(
            enabled: Optional[bool] = Query(None),
            gender: Optional[str] = Query(None)
        ):
            """Test find_by method with filters"""
            conditions = {}
            if enabled is not None:
                conditions["enabled"] = enabled
            if gender:
                conditions["gender"] = gender
            
            users = await self._user_repository.find_by(**conditions)
            return {
                "conditions": conditions,
                "count": len(users),
                "users": [u.to_dict() for u in users]
            }
        
        @self.router.get(
            "/test/find-one-by",
            summary="Test find_one_by method",
            description="Test find_one_by with email condition"
        )
        async def test_find_one_by(email: str = Query(...)):
            """Test find_one_by method"""
            user = await self._user_repository.find_one_by(email=email)
            if user:
                return {
                    "found": True,
                    "user": user.to_dict()
                }
            else:
                return {"found": False}
        
        @self.router.get(
            "/test/exists-by",
            summary="Test exists_by method",
            description="Test exists_by with different conditions"
        )
        async def test_exists_by(
            email: Optional[str] = Query(None),
            username: Optional[str] = Query(None)
        ):
            """Test exists_by method"""
            results = {}
            
            if email:
                results["email_exists"] = await self._user_repository.exists_by(email=email)
            if username:
                results["username_exists"] = await self._user_repository.exists_by(username=username)
            
            return results
        
        @self.router.get(
            "/test/count",
            summary="Test count methods",
            description="Test count and count_deleted methods"
        )
        async def test_count():
            """Test count methods"""
            total_count = await self._user_repository.count()
            enabled_count = await self._user_repository.count(enabled=True)
            disabled_count = await self._user_repository.count(enabled=False)
            deleted_count = await self._user_repository.count_deleted()
            
            return {
                "total_active": total_count,
                "enabled": enabled_count,
                "disabled": disabled_count,
                "soft_deleted": deleted_count
            }
        
        @self.router.post(
            "/test/update-by-id/{user_id}",
            summary="Test update_by_id method",
            description="Test update_by_id method"
        )
        async def test_update_by_id(user_id: str):
            """Test update_by_id method"""
            updated_count = await self._user_repository.update_by_id(
                user_id,
                first_name="UpdatedName",
                phone="555-UPDATED"
            )
            return {
                "updated_count": updated_count,
                "user_id": user_id
            }
        
        @self.router.post(
            "/test/update-by",
            summary="Test update_by method", 
            description="Test update_by with conditions"
        )
        async def test_update_by(
            gender: str = Query(..., description="Gender to filter by"),
            phone_prefix: str = Query("555-BULK", description="New phone prefix")
        ):
            """Test update_by method with conditions"""
            updated_count = await self._user_repository.update_by(
                {"gender": gender},
                phone=phone_prefix
            )
            return {
                "updated_count": updated_count,
                "condition": f"gender={gender}",
                "updated_phone": phone_prefix
            }
        
        @self.router.get(
            "/test/transaction",
            summary="Test transaction context manager",
            description="Test transaction rollback on error"
        )
        async def test_transaction():
            """Test transaction context manager"""
            try:
                async with self._user_repository.transaction() as session:
                    # Create a user
                    user = User(
                        email="transaction@test.com",
                        username="transaction_test",
                        first_name="Transaction",
                        enabled=True
                    )
                    saved_user = await self._user_repository.save(user)
                    
                    # Simulate an error to test rollback
                    raise Exception("Simulated error for transaction test")
                    
            except Exception as e:
                # Check if user was NOT created due to rollback
                exists = await self._user_repository.exists_by_email("transaction@test.com")
                return {
                    "transaction_test": "passed" if not exists else "failed",
                    "error_message": str(e),
                    "user_created": exists
                }
        
        @self.router.get(
            "/test/soft-delete/{user_id}",
            summary="Test soft delete operations",
            description="Test soft delete, restore, and find_deleted methods"
        )
        async def test_soft_delete(user_id: str):
            """Test soft delete operations"""
            # First check if user exists
            user = await self._user_repository.find_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Soft delete the user
            deleted = await self._user_repository.delete_by_id(user_id)
            
            # Check if user is in deleted list
            deleted_users = await self._user_repository.find_deleted()
            deleted_user_ids = [u.id for u in deleted_users]
            
            # Restore the user
            restored = await self._user_repository.restore_by_id(user_id)
            
            # Check if user is back in normal list
            restored_user = await self._user_repository.find_by_id(user_id)
            
            return {
                "soft_delete_success": deleted,
                "found_in_deleted_list": str(user_id) in [str(uid) for uid in deleted_user_ids],
                "restore_success": restored,
                "user_restored": restored_user is not None,
                "final_status": "active" if restored_user else "deleted"
            }
        
        @self.router.get(
            "/test/pagination",
            summary="Test pagination methods",
            description="Test get_users_paginated method"
        )
        async def test_pagination(
            skip: int = Query(0, ge=0),
            limit: int = Query(3, ge=1, le=10)
        ):
            """Test pagination"""
            users = await self._user_repository.get_users_paginated(skip=skip, limit=limit)
            total_count = await self._user_repository.count()
            
            return {
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "returned": len(users)
                },
                "total_active_users": total_count,
                "users": [u.to_dict() for u in users]
            }
        
        @self.router.delete(
            "/test/cleanup",
            summary="Cleanup test data",
            description="Delete all test users created during testing"
        )
        async def cleanup_test_data():
            """Clean up test data"""
            # Delete users created by tests
            test_emails = [
                "user1@test.com", "user2@test.com", "user3@test.com", 
                "user4@test.com", "user5@test.com",
                "batch1@test.com", "batch2@test.com", "batch3@test.com",
                "transaction@test.com"
            ]
            
            deleted_count = 0
            for email in test_emails:
                try:
                    user = await self._user_repository.find_one_by(email=email)
                    if user:
                        await self._user_repository.delete_by_id(user.id, hard_delete=True)
                        deleted_count += 1
                except:
                    pass
            
            return {
                "message": f"Cleaned up {deleted_count} test users",
                "deleted_count": deleted_count
            }

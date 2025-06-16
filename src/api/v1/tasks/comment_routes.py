"""Task Comment routes."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from src.models.user_models import User
from src.services.task_services import TaskCommentService, get_task_comment_services
from src.schemas.task_schemas import CreateTaskComment, ReadTaskComment, UpdateTaskComment
from src.api.v1.auth.auths import current_active_user
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices, get_activity_service

comment_router = APIRouter(tags=["task comments"])


@comment_router.post(
    "/create/new", status_code=status.HTTP_201_CREATED,
    response_model=Optional[ReadTaskComment]
)
async def create_comment(
    task: CreateTaskComment,
    comment_manager: TaskCommentService = Depends(get_task_comment_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> Optional[ReadTaskComment]:
    """
    Create a new comment.

    Args:
        task (CreateTaskComment): New comment to be created.
        comment_manager (TaskCommentService, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        Optional[ReadTask]: _description_
    """
    try:
        task_data = task.model_dump()
        task_data["user_id"] = user.id
        new_comment = await comment_manager.create_comment(task_data)
        if not new_comment:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error commenting on task"
            )
        data={
            "user_id": new_comment.user_id,
            "comment_id": new_comment.id,
            "task_id": new_comment.task_id,
            "description": f"A new comment {str(new_comment.id)} has been created.",
            "activity_type": ActivityType.CREATE,
            "entity": "comment",
            "entity_id": new_comment.id
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return new_comment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e


@comment_router.get(
    "/{comment_id}", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTaskComment]
)
async def get_comment_by_id(
    comment_id: uuid.UUID,
    comment_manager: TaskCommentService = Depends(get_task_comment_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTaskComment]:
    """
    Get a comment by its ID.

    Args:
        comment_id (uuid.UUID): The ID of the comment to retrieve.
        comment_manager (TaskCommentService, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        Optional[ReadTaskComment]: _description_
    """
    try:
        comment = await comment_manager.get_comment_by_id(comment_id, user.id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        return comment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e


@comment_router.get(
    "/task/{task_id}", status_code=status.HTTP_200_OK,
    response_model=List[ReadTaskComment]
)
async def get_comments_by_task_id(
    task_id: uuid.UUID,
    comment_manager: TaskCommentService = Depends(get_task_comment_services),
    user: User = Depends(current_active_user)
) -> List[ReadTaskComment]:
    """
    Get all comments for a specific task.

    Args:
        task_id (uuid.UUID): The ID of the task to retrieve comments for.
        comment_manager (TaskCommentService, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Raises:
        HTTPException: If the task is not found or if an internal server error occurs.

    Returns:
        List[ReadTaskComment]: A list of comments associated with the task.
    """
    try:
        comments = await comment_manager.get_comments_by_task_id(task_id, user.id)
        if not comments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comments not found"
            )
        return comments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e


@comment_router.patch(
    "/{comment_id}/update", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTaskComment]
)
async def update_comment(
    comment_id: uuid.UUID,
    comment: UpdateTaskComment,
    comment_manager: TaskCommentService = Depends(get_task_comment_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> Optional[ReadTaskComment]:
    """
    Update a comment.

    Args:
        comment_id (uuid.UUID): The ID of the comment to update.
        comment (UpdateTaskComment): The data to update the comment with.
        comment_manager (TaskCommentService, optional): Defaults to Depends(get_task_comment_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        Optional[ReadTaskComment]: The updated comment. Or None if the comment was not found.

    Raises:
        HTTPException: If the comment is not found or if an internal server error occurs.
    """
    try:
        comment_data = comment.model_dump()
        updated_comment = await comment_manager.update_comment(
            comment_id, user.id, comment_data
        )
        if not updated_comment:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error updating comment"
            )
        data={
            "user_id": updated_comment.user_id,
            "comment_id": updated_comment.id,
            "task_id": updated_comment.task_id,
            "description": f"Comment with id {str(updated_comment.id)} has been updated.",
            "activity_type": ActivityType.UPDATE,
            "entity": "comment",
            "entity_id": updated_comment.id
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return updated_comment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e


@comment_router.delete(
    "/{comment_id}/delete", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    comment_id: uuid.UUID,
    comment_manager: TaskCommentService = Depends(get_task_comment_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> None:
    """
    Delete a comment by its ID.

    Args:
        comment_id (uuid.UUID): The ID of the comment to delete.
        comment_manager (TaskCommentService, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Raises:
        HTTPException: If the comment is not found or if an internal server error occurs.

    Returns:
        None
    """
    try:
        is_deleted = await comment_manager.delete_comment(comment_id, user.id)
        if not is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        data={
            "user_id": is_deleted.user_id,
            "comment_id": comment_id,
            "task_id": is_deleted.task_id,
            "description": f"Comment with id {str(comment_id)} has been deleted.",
            "activity_type": ActivityType.DELETE,
            "entity": "comment",
            "entity_id": comment_id
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e

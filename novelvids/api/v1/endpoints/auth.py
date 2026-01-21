"""认证相关的 API 端点。"""

from fastapi import APIRouter, Depends, HTTPException, status

from novelvids.application.dto import TokenDTO, UserCreateDTO, UserResponseDTO, LoginDTO, RefreshTokenDTO
from novelvids.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from novelvids.infrastructure.database.repositories import TortoiseUserRepository

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreateDTO):
    """注册新用户。"""
    user_repo = TortoiseUserRepository()

    # 检查用户是否已存在
    existing_email = await user_repo.get_by_email(data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )

    existing_username = await user_repo.get_by_username(data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被占用",
        )

    # 创建用户
    user = await user_repo.create(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    return UserResponseDTO.model_validate(user)


@router.post("/login", response_model=TokenDTO)
async def login(data: LoginDTO):
    """登录并获取访问令牌。"""
    user_repo = TortoiseUserRepository()

    # 通过用户名或邮箱查找用户
    user = await user_repo.get_by_username(data.username)
    if user is None:
        user = await user_repo.get_by_email(data.username)

    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的凭据",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用",
        )

    # 创建令牌
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenDTO(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenDTO)
async def refresh_token(data: RefreshTokenDTO):
    """刷新访问令牌。"""
    try:
        payload = verify_refresh_token(data.refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
            )

        # 创建新令牌
        access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})

        return TokenDTO(access_token=access_token, refresh_token=new_refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e

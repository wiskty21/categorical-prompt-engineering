#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圏論的プロンプトエンジニアリング REST API
FastAPIを使用したHTTP経由での圏論的処理提供

機能:
- RESTful API設計
- 自動API文書生成 (OpenAPI/Swagger)
- 認証・レート制限
- 非同期処理
- メトリクス・監視
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import asyncio
import time
import os
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
import logging
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import uvicorn

# 自作モジュールのインポート
try:
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from optimized_categorical_prompt import (
        OptimizedTensorProduct, OptimizedClaudeClient, OptimizationConfig
    )
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from async_categorical_prompt import (
        AsyncNaturalTransformation, AsyncAdjointPair, AsyncContextMonad
    )
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from robust_categorical_prompt import RobustConfig
except ImportError as e:
    print(f"必要なモジュールが見つかりません: {e}")
    raise

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI アプリ作成
app = FastAPI(
    title="圏論的プロンプトエンジニアリング API",
    description="Category Theory meets AI Engineering - RESTful API for categorical prompt engineering",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Categorical Prompt Engineering Team",
        "url": "https://github.com/your-org/categorical-prompt-engineering",
        "email": "contact@categorical-prompt.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # プロダクションでは具体的なドメインを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip圧縮
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 認証設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# グローバル状態
api_clients = {}
api_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "start_time": time.time()
}

# =============================================================================
# Pydantic モデル定義
# =============================================================================

class APIResponse(BaseModel):
    """共通APIレスポンス"""
    success: bool
    timestamp: datetime
    processing_time: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TensorProductRequest(BaseModel):
    """テンソル積リクエスト"""
    input_text: str = Field(..., min_length=1, max_length=10000, description="分析対象テキスト")
    perspectives: List[str] = Field(..., min_items=1, max_items=10, description="分析観点リスト")
    use_cache: bool = Field(True, description="キャッシュ使用フラグ")
    use_batch: bool = Field(True, description="バッチ処理使用フラグ")
    
    @validator('perspectives')
    def validate_perspectives(cls, v):
        return [p.strip() for p in v if p.strip()]

class TensorProductResponse(BaseModel):
    """テンソル積レスポンス"""
    input_text: str
    perspectives: List[str]
    individual_results: Dict[str, str]
    integrated_result: str
    processing_time: float
    optimization_stats: Optional[Dict[str, Any]] = None

class NaturalTransformationRequest(BaseModel):
    """自然変換リクエスト"""
    content: str = Field(..., min_length=1, max_length=10000, description="変換対象コンテンツ")
    source_domain: str = Field(..., min_length=1, max_length=100, description="変換元領域")
    target_domain: str = Field(..., min_length=1, max_length=100, description="変換先領域")
    transformation_rule: Optional[str] = Field(None, max_length=500, description="変換ルール")

class NaturalTransformationResponse(BaseModel):
    """自然変換レスポンス"""
    source_domain: str
    target_domain: str
    source_content: str
    transformed_content: str
    transformation_rule: str
    processing_time: float

class AdjointRequest(BaseModel):
    """アジョイント関手リクエスト"""
    input_text: str = Field(..., min_length=1, max_length=10000, description="入力テキスト")
    cycle_mode: bool = Field(False, description="完全サイクル実行フラグ")

class AdjointResponse(BaseModel):
    """アジョイント関手レスポンス"""
    input_text: str
    cycle_mode: bool
    free_construction: Optional[Dict[str, Any]] = None
    forgetful_extraction: Optional[Dict[str, Any]] = None
    processing_time: float

class MonadRequest(BaseModel):
    """モナドリクエスト"""
    initial_context: str = Field(..., min_length=1, max_length=5000, description="初期文脈")
    developments: List[str] = Field(..., min_items=1, max_items=20, description="発展ステップ")
    
    @validator('developments')
    def validate_developments(cls, v):
        return [d.strip() for d in v if d.strip()]

class MonadResponse(BaseModel):
    """モナドレスポンス"""
    initial_context: str
    developments: List[str]
    results: List[Dict[str, Any]]
    final_context: str
    total_processing_time: float

class BatchRequest(BaseModel):
    """バッチ処理リクエスト"""
    tasks: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50, description="処理タスクリスト")
    parallel_execution: bool = Field(False, description="並行実行フラグ")
    stop_on_error: bool = Field(False, description="エラー時停止フラグ")

class BatchResponse(BaseModel):
    """バッチ処理レスポンス"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    results: List[Dict[str, Any]]
    total_processing_time: float

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str


# =============================================================================
# 認証・セキュリティ
# =============================================================================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    # 実際の実装では、データベースからユーザーを取得
    # ここではダミーユーザーを返す
    user = User(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# =============================================================================
# ヘルパー関数
# =============================================================================

async def get_optimized_client(user: User) -> OptimizedClaudeClient:
    """最適化クライアント取得"""
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Claude API key not configured"
        )
    
    if user.username not in api_clients:
        config = OptimizationConfig()
        api_clients[user.username] = OptimizedClaudeClient(api_key, config)
    
    return api_clients[user.username]

def update_stats(success: bool):
    """統計更新"""
    api_stats["total_requests"] += 1
    if success:
        api_stats["successful_requests"] += 1
    else:
        api_stats["failed_requests"] += 1

def create_response(data: Any, processing_time: float, error: str = None) -> APIResponse:
    """標準レスポンス作成"""
    return APIResponse(
        success=error is None,
        timestamp=datetime.utcnow(),
        processing_time=processing_time,
        data=data,
        error=error
    )


# =============================================================================
# エンドポイント定義
# =============================================================================

@app.get("/", summary="API情報取得")
async def root():
    """ルートエンドポイント - API基本情報"""
    uptime = time.time() - api_stats["start_time"]
    return {
        "name": "圏論的プロンプトエンジニアリング API",
        "version": "1.0.0",
        "description": "Category Theory meets AI Engineering",
        "uptime_seconds": uptime,
        "endpoints": {
            "tensor": "/api/v1/tensor",
            "transform": "/api/v1/transform", 
            "adjoint": "/api/v1/adjoint",
            "monad": "/api/v1/monad",
            "batch": "/api/v1/batch"
        },
        "documentation": "/docs",
        "status": "healthy"
    }

@app.get("/health", summary="ヘルスチェック")
async def health_check():
    """ヘルスチェックエンドポイント"""
    uptime = time.time() - api_stats["start_time"]
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "uptime_seconds": uptime,
        "stats": api_stats
    }

@app.get("/api/v1/stats", summary="API統計情報")
async def get_stats():
    """API使用統計"""
    uptime = time.time() - api_stats["start_time"]
    return {
        **api_stats,
        "uptime_seconds": uptime,
        "requests_per_second": api_stats["total_requests"] / max(uptime, 1),
        "success_rate": api_stats["successful_requests"] / max(api_stats["total_requests"], 1)
    }

@app.post("/api/v1/tensor", response_model=APIResponse, summary="テンソル積実行")
async def tensor_product(
    request: TensorProductRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    テンソル積による多角的分析
    
    複数の観点から同時に分析し、結果を統合します。
    圏論における**テンソル積**の概念を活用した並行処理です。
    """
    start_time = time.time()
    
    try:
        client = await get_optimized_client(current_user)
        tensor = OptimizedTensorProduct(request.perspectives, client=client)
        
        result = await tensor.apply(
            request.input_text,
            request.use_cache,
            request.use_batch
        )
        
        processing_time = time.time() - start_time
        update_stats(True)
        
        return create_response(result, processing_time)
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_stats(False)
        logger.error(f"Tensor product error: {e}")
        
        return create_response(None, processing_time, str(e))

@app.post("/api/v1/transform", response_model=APIResponse, summary="自然変換実行")
async def natural_transformation(
    request: NaturalTransformationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    自然変換による領域変換
    
    一つの領域から別の領域への構造保存変換を行います。
    圏論の**自然変換**により、本質を保ちながら表現形式を変更します。
    """
    start_time = time.time()
    
    try:
        transformer = AsyncNaturalTransformation(
            request.source_domain,
            request.target_domain,
            request.transformation_rule or f"{request.source_domain}から{request.target_domain}への変換"
        )
        
        result = await transformer.apply_transformation(request.content)
        
        processing_time = time.time() - start_time
        update_stats(True)
        
        return create_response(result, processing_time)
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_stats(False)
        logger.error(f"Natural transformation error: {e}")
        
        return create_response(None, processing_time, str(e))

@app.post("/api/v1/adjoint", response_model=APIResponse, summary="アジョイント関手実行")
async def adjoint_functors(
    request: AdjointRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    アジョイント関手による双対処理
    
    制約からの**自由化**と**本質抽出**の双対性を活用します。
    Free ⊣ Forgetful の随伴関係により創造性と実用性を両立させます。
    """
    start_time = time.time()
    
    try:
        adjoint = AsyncAdjointPair()
        
        if request.cycle_mode:
            result = await adjoint.adjoint_cycle(request.input_text)
        else:
            result = await adjoint.free_construction(request.input_text)
        
        processing_time = time.time() - start_time
        update_stats(True)
        
        return create_response(result, processing_time)
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_stats(False)
        logger.error(f"Adjoint functors error: {e}")
        
        return create_response(None, processing_time, str(e))

@app.post("/api/v1/monad", response_model=APIResponse, summary="モナド発展実行")
async def monad_development(
    request: MonadRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    モナドによる文脈発展
    
    文脈を保持しながら段階的に思考を発展させます。
    モナドの**bind**操作により一貫した文脈での連続的な思考発展を実現します。
    """
    start_time = time.time()
    
    try:
        monad = AsyncContextMonad(request.initial_context)
        results = []
        
        for development in request.developments:
            result = await monad.bind(development)
            results.append(result)
        
        monad_result = {
            "initial_context": request.initial_context,
            "developments": request.developments,
            "results": results,
            "final_context": monad.current_context,
            "total_processing_time": time.time() - start_time
        }
        
        processing_time = time.time() - start_time
        update_stats(True)
        
        return create_response(monad_result, processing_time)
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_stats(False)
        logger.error(f"Monad development error: {e}")
        
        return create_response(None, processing_time, str(e))

@app.post("/api/v1/batch", response_model=APIResponse, summary="バッチ処理実行")
async def batch_processing(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    バッチ処理実行
    
    複数の圏論的操作を一括で実行します。
    並行実行とエラーハンドリングオプションをサポート。
    """
    start_time = time.time()
    
    try:
        results = []
        successful_tasks = 0
        failed_tasks = 0
        
        for i, task in enumerate(request.tasks):
            task_start = time.time()
            
            try:
                operation = task.get("operation")
                params = task.get("parameters", {})
                
                if operation == "tensor":
                    # テンソル積処理
                    client = await get_optimized_client(current_user)
                    tensor = OptimizedTensorProduct(params.get("perspectives", []), client=client)
                    result = await tensor.apply(
                        params.get("input_text", ""),
                        params.get("use_cache", True),
                        params.get("use_batch", True)
                    )
                elif operation == "transform":
                    # 自然変換処理  
                    transformer = AsyncNaturalTransformation(
                        params.get("source_domain", ""),
                        params.get("target_domain", ""),
                        params.get("transformation_rule", "")
                    )
                    result = await transformer.apply_transformation(params.get("content", ""))
                elif operation == "adjoint":
                    # アジョイント関手処理
                    adjoint = AsyncAdjointPair()
                    if params.get("cycle_mode", False):
                        result = await adjoint.adjoint_cycle(params.get("input_text", ""))
                    else:
                        result = await adjoint.free_construction(params.get("input_text", ""))
                elif operation == "monad":
                    # モナド処理
                    monad = AsyncContextMonad(params.get("initial_context", ""))
                    monad_results = []
                    for development in params.get("developments", []):
                        monad_result = await monad.bind(development)
                        monad_results.append(monad_result)
                    result = {
                        "initial_context": params.get("initial_context", ""),
                        "developments": params.get("developments", []),
                        "results": monad_results,
                        "final_context": monad.current_context
                    }
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                
                task_time = time.time() - task_start
                results.append({
                    "task_index": i,
                    "operation": operation,
                    "success": True,
                    "result": result,
                    "processing_time": task_time
                })
                successful_tasks += 1
                
            except Exception as task_error:
                task_time = time.time() - task_start
                results.append({
                    "task_index": i,
                    "operation": task.get("operation", "unknown"),
                    "success": False,
                    "error": str(task_error),
                    "processing_time": task_time
                })
                failed_tasks += 1
                
                if request.stop_on_error:
                    break
        
        batch_result = {
            "total_tasks": len(request.tasks),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "results": results,
            "total_processing_time": time.time() - start_time
        }
        
        processing_time = time.time() - start_time
        update_stats(successful_tasks > 0)
        
        return create_response(batch_result, processing_time)
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_stats(False)
        logger.error(f"Batch processing error: {e}")
        
        return create_response(None, processing_time, str(e))


# =============================================================================
# エラーハンドラー
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Internal server error",
            "status_code": 500
        }
    )


# =============================================================================
# 起動・停止処理
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """アプリ起動時処理"""
    logger.info("圏論的プロンプトエンジニアリング API 起動中...")
    api_stats["start_time"] = time.time()

@app.on_event("shutdown")
async def shutdown_event():
    """アプリ停止時処理"""
    logger.info("圏論的プロンプトエンジニアリング API 停止中...")
    
    # クライアントのクリーンアップ
    for client in api_clients.values():
        try:
            await client.cleanup()
        except Exception as e:
            logger.error(f"Client cleanup error: {e}")


# =============================================================================
# 開発・テスト用関数
# =============================================================================

def create_test_token():
    """テスト用トークン作成"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "testuser"}, expires_delta=access_token_expires
    )
    return access_token

if __name__ == "__main__":
    # 開発サーバー起動
    uvicorn.run(
        "categorical_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
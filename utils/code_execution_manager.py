"""Code execution manager with automatic fallback system."""

from typing import Any, Dict, Optional
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionBackend(Enum):
    """Available code execution backends."""
    JUPYTER = "jupyter"
    CODE_EXECUTOR = "code_executor"


class CodeExecutionManager:
    """Manages code execution with automatic fallback."""

    def __init__(
        self,
        jupyter_client=None,
        code_executor_client=None,
        prefer_notebook: bool = True,
    ):
        """Initialize execution manager.

        Args:
            jupyter_client: JupyterMCPClient instance (primary)
            code_executor_client: CodeExecutorMCPClient instance (fallback)
            prefer_notebook: Whether to prefer notebook execution when available
        """
        self.jupyter_client = jupyter_client
        self.code_executor_client = code_executor_client
        self.prefer_notebook = prefer_notebook
        self._jupyter_available = jupyter_client is not None
        self._code_executor_available = code_executor_client is not None
        self._last_successful_backend = None

        logger.info(
            f"CodeExecutionManager initialized: "
            f"Jupyter={'✓' if self._jupyter_available else '✗'}, "
            f"CodeExecutor={'✓' if self._code_executor_available else '✗'}"
        )

    def execute_code(
        self,
        code: str,
        timeout: Optional[int] = 60,
        use_notebook: Optional[bool] = None,
        force_backend: Optional[ExecutionBackend] = None,
    ) -> Dict[str, Any]:
        """Execute code with automatic fallback.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            use_notebook: Override prefer_notebook setting
            force_backend: Force specific backend (bypass fallback)

        Returns:
            Execution result dictionary with:
                - success: bool
                - output: str or dict
                - backend: ExecutionBackend used
                - error: Optional error message

        Raises:
            Exception: If all execution methods fail
        """
        if use_notebook is None:
            use_notebook = self.prefer_notebook

        if force_backend:
            return self._execute_with_backend(
                backend=force_backend,
                code=code,
                timeout=timeout,
                use_notebook=use_notebook,
            )

        if use_notebook and self._jupyter_available:
            try:
                result = self._execute_jupyter(code, timeout)
                self._last_successful_backend = ExecutionBackend.JUPYTER
                return result
            except Exception as e:
                logger.warning(f"Jupyter execution failed: {e}")
                logger.info("Attempting fallback to Code Executor...")

        if self._code_executor_available:
            try:
                result = self._execute_code_executor(code, timeout)
                self._last_successful_backend = ExecutionBackend.CODE_EXECUTOR
                return result
            except Exception as e:
                logger.error(f"Code Executor failed: {e}")

        if not use_notebook and self._jupyter_available:
            try:
                logger.info("Attempting Jupyter as last resort...")
                result = self._execute_jupyter(code, timeout)
                self._last_successful_backend = ExecutionBackend.JUPYTER
                return result
            except Exception as e:
                logger.error(f"Jupyter (last resort) failed: {e}")

        raise Exception("All code execution backends failed")

    def _execute_with_backend(
        self,
        backend: ExecutionBackend,
        code: str,
        timeout: int,
        use_notebook: bool,
    ) -> Dict[str, Any]:
        """Execute with specific backend."""
        if backend == ExecutionBackend.JUPYTER:
            if not self._jupyter_available:
                raise Exception("Jupyter backend not available")
            return self._execute_jupyter(code, timeout)
        elif backend == ExecutionBackend.CODE_EXECUTOR:
            if not self._code_executor_available:
                raise Exception("Code Executor backend not available")
            return self._execute_code_executor(code, timeout)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def _execute_jupyter(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code using Jupyter MCP."""
        logger.info("Executing code with Jupyter MCP...")

        try:
            result = self.jupyter_client.insert_execute_code_cell(
                cell_index=-1,
                cell_source=code,
                timeout=timeout,
            )

            logger.info("✓ Jupyter execution successful")

            return {
                "success": True,
                "output": result,
                "backend": ExecutionBackend.JUPYTER,
                "error": None,
            }

        except Exception as e:
            logger.error(f"✗ Jupyter execution failed: {e}")
            raise

    def _execute_code_executor(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code using Code Executor MCP."""
        logger.info("Executing code with Code Executor MCP...")

        try:
            result = self.code_executor_client.execute_code(
                code=code,
                timeout=timeout,
            )

            logger.info("✓ Code Executor execution successful")

            return {
                "success": True,
                "output": result,
                "backend": ExecutionBackend.CODE_EXECUTOR,
                "error": None,
            }

        except Exception as e:
            logger.error(f"✗ Code Executor execution failed: {e}")
            raise

    def get_backend_status(self) -> Dict[str, Any]:
        """Get status of all backends.

        Returns:
            Status dictionary with availability info
        """
        status = {
            "jupyter": {
                "available": self._jupyter_available,
                "status": "unknown",
            },
            "code_executor": {
                "available": self._code_executor_available,
                "status": "unknown",
            },
            "last_successful": self._last_successful_backend.value
            if self._last_successful_backend
            else None,
        }

        if self._jupyter_available:
            try:
                tools = self.jupyter_client.list_tools()
                status["jupyter"]["status"] = "healthy"
                status["jupyter"]["tools_count"] = len(tools)
            except Exception as e:
                status["jupyter"]["status"] = f"error: {e}"

        if self._code_executor_available:
            try:
                tools = self.code_executor_client.list_tools()
                status["code_executor"]["status"] = "healthy"
                status["code_executor"]["tools_count"] = len(tools)
            except Exception as e:
                status["code_executor"]["status"] = f"error: {e}"

        return status

    def test_backends(self) -> Dict[str, Any]:
        """Test all available backends with simple code.

        Returns:
            Test results for each backend
        """
        test_code = "print('Backend test successful')\nresult = 2 + 2\nprint(f'2 + 2 = {result}')"

        results = {}

        if self._jupyter_available:
            try:
                result = self._execute_jupyter(test_code, timeout=10)
                results["jupyter"] = {
                    "success": True,
                    "output": result.get("output"),
                }
            except Exception as e:
                results["jupyter"] = {
                    "success": False,
                    "error": str(e),
                }

        if self._code_executor_available:
            try:
                result = self._execute_code_executor(test_code, timeout=10)
                results["code_executor"] = {
                    "success": True,
                    "output": result.get("output"),
                }
            except Exception as e:
                results["code_executor"] = {
                    "success": False,
                    "error": str(e),
                }

        return results

    def close(self):
        """Close all MCP client connections."""
        if self.jupyter_client:
            try:
                self.jupyter_client.close()
                logger.info("Closed Jupyter MCP client")
            except Exception as e:
                logger.warning(f"Error closing Jupyter client: {e}")

        if self.code_executor_client:
            try:
                self.code_executor_client.close()
                logger.info("Closed Code Executor MCP client")
            except Exception as e:
                logger.warning(f"Error closing Code Executor client: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

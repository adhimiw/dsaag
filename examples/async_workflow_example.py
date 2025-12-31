"""
Example: Asynchronous Dataset Analysis Workflow

This example demonstrates:
1. Using CrewAI's async kickoff for concurrent execution
2. Code execution with automatic fallback (Jupyter -> Code Executor)
3. Browser automation with Chrome DevTools for web research
4. Parallel dataset analysis with multiple crews
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings
from llm.factory import get_llm
from mcp_clients import (
    JupyterMCPClient,
    CodeExecutorMCPClient,
    BrowserMCPClient,
    FilesystemMCPClient,
)
from utils.code_execution_manager import CodeExecutionManager
from utils.logger import setup_logger, get_logger
from crewai import Crew, Agent, Task, Process

setup_logger(log_level="INFO")
logger = get_logger(__name__)


async def main():
    """Main async workflow demonstration."""
    
    logger.info("=" * 60)
    logger.info("Starting Async Dataset Analysis Workflow")
    logger.info("=" * 60)
    
    settings = get_settings()
    primary_llm = get_llm(provider=settings.primary_llm_provider)
    
    logger.info("\n1. Initializing MCP Clients with Fallback System...")
    logger.info("-" * 60)
    
    jupyter_client = JupyterMCPClient(
        server_path=settings.jupyter_mcp_server_path,
        transport=settings.mcp_server_transport,
        env={
            "JUPYTER_URL": settings.jupyter_url,
            "JUPYTER_TOKEN": settings.jupyter_token or "",
            "ALLOW_IMG_OUTPUT": "true"
        }
    )
    
    code_executor_client = CodeExecutorMCPClient(
        server_path=["node", str(Path.cwd() / "mcp_code_executor" / "build" / "index.js")],
        transport=settings.mcp_server_transport,
        env={
            "CODE_STORAGE_DIR": str(Path.cwd() / "code_storage"),
            "CONDA_ENV_NAME": "base"
        }
    )
    
    browser_client = BrowserMCPClient(
        server_path=settings.browser_mcp_server_path,
        transport=settings.mcp_server_transport,
    )
    
    filesystem_client = FilesystemMCPClient(
        server_path=settings.filesystem_mcp_server_path,
        transport=settings.mcp_server_transport,
    )
    
    code_exec_manager = CodeExecutionManager(
        jupyter_client=jupyter_client,
        code_executor_client=code_executor_client,
        prefer_notebook=True,
    )
    
    logger.info("✓ All MCP clients initialized")
    
    logger.info("\n2. Testing Backend Status...")
    logger.info("-" * 60)
    
    backend_status = code_exec_manager.get_backend_status()
    for backend, status in backend_status.items():
        if isinstance(status, dict):
            logger.info(f"  {backend}: {status.get('status', 'unknown')}")
    
    logger.info("\n3. Creating Specialized Agents...")
    logger.info("-" * 60)
    
    eda_agent = Agent(
        role="Exploratory Data Analyst",
        goal="Perform comprehensive EDA on datasets with statistical analysis",
        backstory="You are an expert data scientist specializing in exploratory data analysis",
        llm=primary_llm,
        verbose=True
    )
    
    web_research_agent = Agent(
        role="Web Data Researcher",
        goal="Gather contextual data from web sources using browser automation",
        backstory="You are an expert in web scraping and data collection with Chrome DevTools",
        llm=primary_llm,
        verbose=True
    )
    
    modeling_agent = Agent(
        role="Predictive Modeler",
        goal="Build and evaluate predictive models",
        backstory="You are an expert in machine learning and model optimization",
        llm=primary_llm,
        verbose=True
    )
    
    logger.info("✓ Agents created")
    
    logger.info("\n4. Defining Tasks...")
    logger.info("-" * 60)
    
    eda_task = Task(
        description="""
        Analyze the dataset at data/churn.csv.
        1. Load the data using pandas
        2. Display basic statistics (shape, dtypes, describe())
        3. Check for missing values
        4. Generate correlation matrix
        5. Create visualizations (if possible)
        
        Use the code execution system which will automatically fallback if needed.
        """,
        agent=eda_agent,
        expected_output="Comprehensive EDA report with insights and statistics"
    )
    
    web_task = Task(
        description="""
        Research customer churn trends in the telecommunications industry.
        1. Navigate to relevant industry websites
        2. Extract key statistics and insights
        3. Capture performance metrics of the sites
        4. Monitor API calls made by the sites
        
        Use Chrome DevTools capabilities explicitly.
        """,
        agent=web_research_agent,
        expected_output="Industry insights with citations and metrics"
    )
    
    modeling_task = Task(
        description="""
        Build a predictive model for the churn dataset.
        1. Load and preprocess data
        2. Split into train/test sets
        3. Train a logistic regression model
        4. Evaluate performance (accuracy, precision, recall)
        5. Report feature importance
        
        Use the code execution system with automatic fallback.
        """,
        agent=modeling_agent,
        expected_output="Model performance metrics and evaluation report"
    )
    
    logger.info("✓ Tasks defined")
    
    logger.info("\n5. Creating Crews...")
    logger.info("-" * 60)
    
    eda_crew = Crew(
        agents=[eda_agent],
        tasks=[eda_task],
        process=Process.sequential,
        verbose=True
    )
    
    web_crew = Crew(
        agents=[web_research_agent],
        tasks=[web_task],
        process=Process.sequential,
        verbose=True
    )
    
    modeling_crew = Crew(
        agents=[modeling_agent],
        tasks=[modeling_task],
        process=Process.sequential,
        verbose=True
    )
    
    logger.info("✓ Crews created")
    
    logger.info("\n6. Executing Crews Concurrently with akickoff()...")
    logger.info("-" * 60)
    logger.info("This demonstrates parallel execution of multiple analysis tasks")
    
    try:
        import os
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "sk-dummy-key-not-used"
        
        results = await asyncio.gather(
            eda_crew.akickoff(inputs={}),
            web_crew.akickoff(inputs={}),
            modeling_crew.akickoff(inputs={}),
            return_exceptions=True
        )
        
        logger.info("\n7. Results Summary...")
        logger.info("=" * 60)
        
        eda_result, web_result, modeling_result = results
        
        if not isinstance(eda_result, Exception):
            logger.info("\n✓ EDA Crew Result:")
            logger.info(str(eda_result)[:500] + "..." if len(str(eda_result)) > 500 else str(eda_result))
        else:
            logger.error(f"\n✗ EDA Crew Failed: {eda_result}")
        
        if not isinstance(web_result, Exception):
            logger.info("\n✓ Web Research Crew Result:")
            logger.info(str(web_result)[:500] + "..." if len(str(web_result)) > 500 else str(web_result))
        else:
            logger.error(f"\n✗ Web Research Crew Failed: {web_result}")
        
        if not isinstance(modeling_result, Exception):
            logger.info("\n✓ Modeling Crew Result:")
            logger.info(str(modeling_result)[:500] + "..." if len(str(modeling_result)) > 500 else str(modeling_result))
        else:
            logger.error(f"\n✗ Modeling Crew Failed: {modeling_result}")
        
    except Exception as e:
        logger.error(f"Error during async execution: {e}", exc_info=True)
    
    finally:
        logger.info("\n8. Cleanup...")
        logger.info("-" * 60)
        
        code_exec_manager.close()
        browser_client.close()
        filesystem_client.close()
        
        logger.info("✓ All clients closed")
    
    logger.info("\n" + "=" * 60)
    logger.info("Async Workflow Complete!")
    logger.info("=" * 60)


async def demonstrate_code_execution_fallback():
    """Demonstrate code execution with automatic fallback."""
    
    logger.info("\n" + "=" * 60)
    logger.info("Code Execution Fallback Demonstration")
    logger.info("=" * 60)
    
    settings = get_settings()
    
    jupyter_client = JupyterMCPClient()
    code_executor_client = CodeExecutorMCPClient()
    
    code_exec_manager = CodeExecutionManager(
        jupyter_client=jupyter_client,
        code_executor_client=code_executor_client,
    )
    
    test_code = """
import pandas as pd
import numpy as np

data = {
    'A': [1, 2, 3, 4, 5],
    'B': [10, 20, 30, 40, 50]
}

df = pd.DataFrame(data)
print("DataFrame created:")
print(df)
print(f"\\nMean of column A: {df['A'].mean()}")
print(f"Sum of column B: {df['B'].sum()}")
"""
    
    logger.info("\n1. Testing Code Execution...")
    logger.info("-" * 60)
    
    try:
        result = code_exec_manager.execute_code(code=test_code, timeout=30)
        
        logger.info(f"✓ Execution successful using: {result['backend'].value}")
        logger.info(f"Output: {result['output']}")
        
    except Exception as e:
        logger.error(f"✗ Execution failed: {e}")
    
    finally:
        code_exec_manager.close()


async def demonstrate_browser_automation():
    """Demonstrate enhanced Chrome DevTools capabilities."""
    
    logger.info("\n" + "=" * 60)
    logger.info("Browser Automation with Chrome DevTools")
    logger.info("=" * 60)
    
    browser_client = BrowserMCPClient()
    
    try:
        logger.info("\n1. Navigating to example site...")
        browser_client.navigate_page("https://example.com")
        
        logger.info("\n2. Getting page metadata...")
        metadata = browser_client.get_page_metadata()
        logger.info(f"Title: {metadata.get('title')}")
        logger.info(f"URL: {metadata.get('url')}")
        
        logger.info("\n3. Capturing performance metrics...")
        metrics = browser_client.get_performance_metrics()
        logger.info(f"Performance: {metrics}")
        
        logger.info("\n4. Monitoring network activity...")
        network_logs = browser_client.get_network_logs()
        logger.info(f"Network requests: {len(network_logs)} captured")
        
        logger.info("\n5. Taking screenshot...")
        screenshot_path = str(Path.cwd() / "outputs" / "example_screenshot.png")
        browser_client.take_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to: {screenshot_path}")
        
    except Exception as e:
        logger.error(f"Browser automation error: {e}", exc_info=True)
    
    finally:
        browser_client.close()


if __name__ == "__main__":
    print("\nChoose a demonstration:")
    print("1. Full Async Workflow (CrewAI + Fallback + Browser)")
    print("2. Code Execution Fallback Only")
    print("3. Browser Automation Only")
    print("4. All Demonstrations")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(demonstrate_code_execution_fallback())
    elif choice == "3":
        asyncio.run(demonstrate_browser_automation())
    elif choice == "4":
        asyncio.run(demonstrate_code_execution_fallback())
        asyncio.run(demonstrate_browser_automation())
        asyncio.run(main())
    else:
        print("Invalid choice. Running full workflow...")
        asyncio.run(main())

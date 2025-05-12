import logging
from typing import List, Dict, Any, Optional
from .context import NewsContext
from .operators import ContextOperator
from src.analysis import SentimentAnalyzer

logger = logging.getLogger(__name__)

class MCPController:
    """
    Controller for the Model Context Protocol implementation.
    Manages the flow of context through different operators.
    """
    
    def __init__(self):
        self.operators = {}
        
    def register_operator(self, operator: ContextOperator) -> None:
        """Register a context operator with the controller."""
        self.operators[operator.name] = operator
        logger.debug(f"Registered operator: {operator.name}")
    
    def process(self, context: NewsContext, pipeline: List[str]) -> NewsContext:
        """
        Process a context through a pipeline of operators.
        
        Args:
            context: The news context to process
            pipeline: List of operator names to execute in sequence
            
        Returns:
            The processed context
        """
        for operator_name in pipeline:
            if operator_name not in self.operators:
                logger.error(f"Unknown operator: {operator_name}")
                continue
                
            operator = self.operators[operator_name]
            logger.info(f"Executing operator: {operator_name}")
            
            try:
                context = operator.execute(context)
                
                # Log the current state after each operation
                summary = context.get_summary()
                logger.info(f"Context after {operator_name}: {summary}")
                
            except Exception as e:
                logger.error(f"Error executing operator {operator_name}: {e}")
                context.update_state(current_operation=f"error_in_{operator_name}")
        
        return context
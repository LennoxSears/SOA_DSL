"""
Expression Evaluator for SOA DSL.

Evaluates mathematical expressions and conditional logic in constraints.
"""

import re
import math
from typing import Dict, Any, Union, Optional


class ExpressionError(Exception):
    """Exception raised for expression evaluation errors."""
    pass


class ExpressionEvaluator:
    """Evaluates DSL expressions."""
    
    def __init__(self, global_params: Dict[str, Any] = None):
        """
        Initialize evaluator.
        
        Args:
            global_params: Dictionary of global parameter values
        """
        self.global_params = global_params or {}
        self.functions = {
            'min': min,
            'max': max,
            'abs': abs,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pow': pow,
        }
    
    def evaluate(self, expr: Union[str, float, int], context: Dict[str, Any] = None) -> Union[str, float]:
        """
        Evaluate an expression.
        
        Args:
            expr: Expression to evaluate (string or numeric)
            context: Additional context variables (device parameters, etc.)
        
        Returns:
            Evaluated value or original string if cannot evaluate
        """
        # If already numeric, return as-is
        if isinstance(expr, (int, float)):
            return expr
        
        if not isinstance(expr, str):
            return expr
        
        # Merge context with global params
        variables = {**self.global_params}
        if context:
            variables.update(context)
        
        try:
            # Handle conditional expressions (if-then-else)
            if 'if' in expr and 'then' in expr:
                return self._evaluate_conditional(expr, variables)
            
            # Handle function calls
            if any(func in expr for func in self.functions.keys()):
                return self._evaluate_with_functions(expr, variables)
            
            # Handle simple arithmetic
            return self._evaluate_arithmetic(expr, variables)
        
        except Exception as e:
            # If evaluation fails, return original expression as string
            # This allows expressions to be passed through to Spectre
            return expr
    
    def can_evaluate(self, expr: Union[str, float, int]) -> bool:
        """Check if an expression can be evaluated to a constant."""
        if isinstance(expr, (int, float)):
            return True
        
        if not isinstance(expr, str):
            return False
        
        # Check if expression contains only constants and operators
        # No variables, device parameters, or runtime values
        has_variables = bool(re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr))
        has_device_params = '$' in expr
        has_voltage_refs = 'v[' in expr or 'i[' in expr
        has_temp = 'T' in expr or 'temp' in expr
        
        return not (has_variables or has_device_params or has_voltage_refs or has_temp)
    
    def _evaluate_conditional(self, expr: str, variables: Dict[str, Any]) -> Union[str, float]:
        """Evaluate if-then-else conditional expression."""
        # Parse: if CONDITION then VALUE1 else VALUE2
        match = re.match(r'if\s+(.+?)\s+then\s+(.+?)\s+else\s+(.+)', expr, re.IGNORECASE)
        if not match:
            raise ExpressionError(f"Invalid conditional syntax: {expr}")
        
        condition_str, true_val_str, false_val_str = match.groups()
        
        # Evaluate condition
        condition = self._evaluate_condition(condition_str, variables)
        
        # Return appropriate value
        if condition:
            return self.evaluate(true_val_str.strip(), variables)
        else:
            return self.evaluate(false_val_str.strip(), variables)
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate a boolean condition."""
        # Handle comparison operators
        for op in ['<=', '>=', '==', '!=', '<', '>']:
            if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._evaluate_arithmetic(left.strip(), variables)
                right_val = self._evaluate_arithmetic(right.strip(), variables)
                
                if op == '<':
                    return left_val < right_val
                elif op == '<=':
                    return left_val <= right_val
                elif op == '>':
                    return left_val > right_val
                elif op == '>=':
                    return left_val >= right_val
                elif op == '==':
                    return left_val == right_val
                elif op == '!=':
                    return left_val != right_val
        
        # If no operator, evaluate as boolean
        return bool(self._evaluate_arithmetic(condition, variables))
    
    def _evaluate_with_functions(self, expr: str, variables: Dict[str, Any]) -> float:
        """Evaluate expression containing function calls."""
        # Replace function calls with evaluated values
        result_expr = expr
        
        # Find all function calls
        for func_name in self.functions.keys():
            pattern = rf'{func_name}\s*\(([^)]+)\)'
            matches = re.finditer(pattern, result_expr)
            
            for match in matches:
                args_str = match.group(1)
                # Split arguments by comma (simple split, doesn't handle nested functions)
                args = [arg.strip() for arg in args_str.split(',')]
                
                # Evaluate each argument
                eval_args = []
                for arg in args:
                    eval_arg = self._evaluate_arithmetic(arg, variables)
                    eval_args.append(eval_arg)
                
                # Call function
                func = self.functions[func_name]
                result = func(*eval_args)
                
                # Replace in expression
                result_expr = result_expr.replace(match.group(0), str(result))
        
        # Evaluate remaining arithmetic
        return self._evaluate_arithmetic(result_expr, variables)
    
    def _evaluate_arithmetic(self, expr: str, variables: Dict[str, Any]) -> float:
        """Evaluate arithmetic expression."""
        # Replace variables with values
        result_expr = expr
        
        # Replace global parameters
        for var_name, var_value in variables.items():
            # Use word boundaries to avoid partial matches
            pattern = rf'\b{re.escape(var_name)}\b'
            if isinstance(var_value, str):
                # If value is also an expression, recursively evaluate
                var_value = self.evaluate(var_value, variables)
            result_expr = re.sub(pattern, str(var_value), result_expr)
        
        # If expression still contains variables, return as string
        if re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', result_expr):
            # Check if it's a known variable that should be kept
            if any(x in result_expr for x in ['temp', 'T', '$', 'v[', 'i[']):
                return result_expr
            # Otherwise try to evaluate
        
        # Replace ^ with ** for Python
        result_expr = result_expr.replace('^', '**')
        
        try:
            # Safely evaluate arithmetic expression
            # Note: Using eval is generally unsafe, but we control the input
            # In production, use a proper expression parser
            result = eval(result_expr, {"__builtins__": {}}, {})
            return float(result)
        except:
            # If evaluation fails, return original
            return expr
    
    def to_spectre_expression(self, expr: Union[str, float, int]) -> str:
        """
        Convert DSL expression to Spectre syntax.
        
        Args:
            expr: DSL expression
        
        Returns:
            Spectre-compatible expression string
        """
        if isinstance(expr, (int, float)):
            return str(expr)
        
        if not isinstance(expr, str):
            return str(expr)
        
        result = expr
        
        # Convert if-then-else to ternary operator
        if 'if' in result and 'then' in result and 'else' in result:
            match = re.match(r'if\s+(.+?)\s+then\s+(.+?)\s+else\s+(.+)', result, re.IGNORECASE)
            if match:
                condition, true_val, false_val = match.groups()
                # Spectre uses: (condition) ? true_val : false_val
                result = f"({condition}) ? {true_val} : {false_val}"
        
        # Convert device parameters: $w -> w, $l -> l
        result = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', result)
        
        # Convert voltage references: v[d,s] -> V(d,s)
        result = re.sub(r'v\[([a-z_]+),([a-z_]+)\]', r'V(\1,\2)', result)
        result = re.sub(r'v\[([a-z_]+)\]', r'V(\1)', result)
        
        # Convert current references: i[device] -> I(device)
        result = re.sub(r'i\[([a-z_0-9]+)\]', r'I(\1)', result)
        
        # Convert temperature: T or temp -> temp
        result = re.sub(r'\bT\b', 'temp', result)
        
        # Keep ^ as is (Spectre uses ^ for power)
        # Keep other operators as is
        
        return result
    
    def substitute_globals(self, expr: Union[str, float, int]) -> Union[str, float]:
        """
        Substitute global parameter references with their values.
        
        Args:
            expr: Expression with global parameter references
        
        Returns:
            Expression with substituted values
        """
        if isinstance(expr, (int, float)):
            return expr
        
        if not isinstance(expr, str):
            return expr
        
        result = expr
        
        # Replace global parameters
        for param_name, param_value in self.global_params.items():
            pattern = rf'\b{re.escape(param_name)}\b'
            result = re.sub(pattern, str(param_value), result)
        
        return result

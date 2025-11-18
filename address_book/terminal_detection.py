"""
Terminal detection utilities for determining the type of terminal environment.
"""

import os


class TerminalDetector:
    """
    Utility class for detecting terminal types and environments.
    """
    
    @staticmethod
    def is_ide_terminal() -> bool:
        """
        Check if running in an IDE terminal.
        
        Returns:
            True if running in an IDE terminal, False otherwise
        """
        # Check for common IDE environment variables
        ide_indicators = [
            'VSCODE_PID',  # Visual Studio Code
            'PYCHARM_HOSTED',  # PyCharm
            'TERM_PROGRAM=vscode',  # VS Code terminal
            'TERM_PROGRAM=hyper',  # Hyper terminal
            'TERM_PROGRAM=tmux',  # tmux
        ]
        
        for indicator in ide_indicators:
            if '=' in indicator:
                key, value = indicator.split('=', 1)
                if os.environ.get(key) == value:
                    return True
            elif os.environ.get(indicator):
                return True
        
        # Check if TERM is set to a common IDE value
        term = os.environ.get('TERM', '')
        if term in ['xterm-256color', 'xterm-color', 'screen'] and os.name == 'nt':
            # On Windows, these TERM values often indicate an IDE terminal
            # But only if we're not in Windows Terminal
            if not os.environ.get('WT_SESSION'):  # Windows Terminal sets this
                return True
        
        # Additional check: if running on Windows but not in a standard console
        if os.name == 'nt':
            # Check if we're in Windows Terminal
            if os.environ.get('WT_SESSION'):
                return False  # Windows Terminal is a native terminal
            
            # Check if we're in PowerShell or cmd.exe
            shell = os.environ.get('PROMPT', '')
            comspec = os.environ.get('COMSPEC', '')
            
            # PowerShell and cmd.exe are valid native terminals
            # PowerShell might have powershell.exe in COMSPEC instead of cmd.exe
            if (comspec and ('cmd.exe' in comspec.lower() or 'powershell.exe' in comspec.lower())) or shell:
                return False  # This is a native Windows console
            
            # If we get here, we might be in an IDE terminal
            return True
            
        return False
    
    @staticmethod
    def get_terminal_info() -> dict:
        """
        Get detailed information about the current terminal environment.
        
        Returns:
            Dictionary containing terminal information
        """
        info = {
            'os': os.name,
            'ide_detected': TerminalDetector.is_ide_terminal(),
            'environment_variables': {}
        }
        
        # Collect relevant environment variables
        relevant_vars = [
            'TERM', 'TERM_PROGRAM', 'WT_SESSION', 'PROMPT', 'COMSPEC',
            'VSCODE_PID', 'PYCHARM_HOSTED', 'SHELL', 'CONEMUANSI',
            'TERMINAL_EMULATOR'
        ]
        
        for var in relevant_vars:
            value = os.environ.get(var)
            if value:
                info['environment_variables'][var] = value
        
        return info
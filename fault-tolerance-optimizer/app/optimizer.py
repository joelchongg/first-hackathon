# app/optimizer.py
import numpy as np
from sklearn.ensemble import IsolationForest
import psutil
import logging
import os
import time
from datetime import datetime
from collections import deque
import platform

class SystemOptimizer:
    def __init__(self):
        # Initialize components
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Optimization parameters
        self.threshold_critical = 90.0
        self.threshold_warning = 70.0
        
        # History tracking
        self.optimization_history = deque(maxlen=50)
        self.active_optimizations = set()
        
        # Cooldown tracking
        self.last_optimization_time = {}
        self.optimization_cooldown = 300  # 5 minutes
        
        # Setup logging
        self._setup_logging()
        
        # Initialize optimization actions
        self.optimization_actions = self._initialize_actions()

    def _setup_logging(self):
        """Initialize logging configuration"""
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
                
            logging.basicConfig(
                filename='logs/optimizer.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('SystemOptimizer')
        except Exception as e:
            print(f"Error setting up logging: {e}")

    def _initialize_actions(self):
        """Initialize available optimization actions"""
        return {
            'cpu_optimization': {
                'id': 'cpu_opt',
                'name': 'CPU Optimization',
                'description': 'Optimize CPU-intensive processes',
                'function': self._optimize_cpu,
                'cooldown': 300,
                'conditions': lambda m: float(m['cpu_usage']) > self.threshold_warning
            },
            'memory_optimization': {
                'id': 'mem_opt',
                'name': 'Memory Optimization',
                'description': 'Optimize memory usage',
                'function': self._optimize_memory,
                'cooldown': 300,
                'conditions': lambda m: float(m['memory_usage']) > self.threshold_warning
            },
            'disk_optimization': {
                'id': 'disk_opt',
                'name': 'Disk Optimization',
                'description': 'Optimize disk usage',
                'function': self._optimize_disk,
                'cooldown': 300,
                'conditions': lambda m: float(m['disk_usage']) > self.threshold_warning
            }
        }

    def check_system(self, metrics, predictions):
        """Analyze system and determine if optimization is needed"""
        try:
            needed_optimizations = []
            
            # Check each optimization action
            for action in self.optimization_actions.values():
                # Skip if in cooldown
                if (action['id'] in self.last_optimization_time and 
                    time.time() - self.last_optimization_time[action['id']] < action['cooldown']):
                    continue
                
                # Check if conditions are met
                if action['conditions'](metrics):
                    needed_optimizations.append({
                        'id': action['id'],
                        'name': action['name'],
                        'description': action['description'],
                        'priority': self._calculate_priority(metrics, action['id'])
                    })
            
            return needed_optimizations
            
        except Exception as e:
            self.logger.error(f"Error checking system: {e}")
            return []

    def _calculate_priority(self, metrics, action_id):
        """Calculate priority for optimization action"""
        try:
            if action_id.startswith('cpu'):
                value = metrics['cpu_usage']
            elif action_id.startswith('mem'):
                value = metrics['memory_usage']
            elif action_id.startswith('disk'):
                value = metrics['disk_usage']
            else:
                value = 0
                
            if value > self.threshold_critical:
                return 'critical'
            elif value > self.threshold_warning:
                return 'high'
            else:
                return 'medium'
                
        except Exception as e:
            self.logger.error(f"Error calculating priority: {e}")
            return 'medium'

    def optimize(self, action_id, metrics):
        """Execute optimization action"""
        try:
            # Find the requested action
            action = next(
                (a for a in self.optimization_actions.values() if a['id'] == action_id),
                None
            )
            
            if not action:
                return False, "Unknown optimization action"
            
            # Check if action is already running
            if action_id in self.active_optimizations:
                return False, "Optimization already in progress"
            
            # Check cooldown
            if (action_id in self.last_optimization_time and 
                time.time() - self.last_optimization_time[action_id] < action['cooldown']):
                return False, "Optimization in cooldown"
            
            # Execute optimization
            self.active_optimizations.add(action_id)
            success = action['function']()
            self.last_optimization_time[action_id] = time.time()
            
            # Record optimization
            self.optimization_history.append({
                'action_id': action_id,
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'metrics': metrics
            })
            
            # Remove from active optimizations
            self.active_optimizations.discard(action_id)
            
            return success, f"Completed {action['name']}"
            
        except Exception as e:
            self.logger.error(f"Error in optimization: {e}")
            if action_id in self.active_optimizations:
                self.active_optimizations.discard(action_id)
            return False, str(e)

    def _optimize_cpu(self):
        """Optimize CPU usage"""
        try:
            self.logger.info("Starting CPU optimization")
            optimized = False
            
            # Get CPU-intensive processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 50.0:
                        # Reduce priority of CPU-intensive processes
                        if platform.system() == 'Windows':
                            proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                        else:
                            proc.nice(10)
                        optimized = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error in CPU optimization: {e}")
            return False

    def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            self.logger.info("Starting memory optimization")
            optimized = False
            
            # Get memory-intensive processes
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 20.0:
                        if platform.system() == 'Windows':
                            # Trigger garbage collection for Python processes
                            if proc.info['name'].lower().startswith('python'):
                                import gc
                                gc.collect()
                        else:
                            # Request memory trim on Unix systems
                            os.system(f"echo 1 > /proc/{proc.info['pid']}/oom_score_adj")
                        optimized = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error in memory optimization: {e}")
            return False

    def _optimize_disk(self):
        """Optimize disk usage"""
        try:
            self.logger.info("Starting disk optimization")
            optimized = False
            
            # Clean temporary files
            temp_dirs = ['/tmp', '/var/tmp'] if platform.system() != 'Windows' else [
                os.environ.get('TEMP'),
                os.environ.get('TMP')
            ]
            
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        # Remove files older than 1 day
                        current_time = time.time()
                        for item in os.listdir(temp_dir):
                            item_path = os.path.join(temp_dir, item)
                            if os.path.isfile(item_path):
                                if current_time - os.path.getctime(item_path) > 86400:
                                    try:
                                        os.remove(item_path)
                                        optimized = True
                                    except OSError:
                                        continue
                    except OSError:
                        continue
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error in disk optimization: {e}")
            return False

    def get_optimization_status(self):
        """Get current optimization status"""
        return {
            'active_optimizations': list(self.active_optimizations),
            'recent_history': list(self.optimization_history)[-5:],
            'cooldowns': {
                action['id']: max(0, action['cooldown'] - 
                    (time.time() - self.last_optimization_time.get(action['id'], 0)))
                for action in self.optimization_actions.values()
            }
        }

    def get_available_actions(self):
        """Get list of available optimization actions"""
        return [
            {
                'id': action['id'],
                'name': action['name'],
                'description': action['description'],
                'cooldown': action['cooldown'],
                'cooldown_remaining': max(0, action['cooldown'] - 
                    (time.time() - self.last_optimization_time.get(action['id'], 0)))
            }
            for action in self.optimization_actions.values()
        ]

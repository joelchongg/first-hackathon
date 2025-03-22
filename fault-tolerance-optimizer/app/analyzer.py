class SystemAnalyzer:
    def __init__(self):
        self.metrics_history = []
        self.threshold = 80.0  # Set threshold as float

    def analyze_metrics(self, metrics):
        if 'error' in metrics:
            return True

        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
        
        # Check numeric metrics against threshold
        return any(
            float(value) > self.threshold 
            for key, value in metrics.items() 
            if isinstance(value, (int, float)) and 'time' not in key.lower()
        )

    def get_system_health_score(self):
        if not self.metrics_history:
            return 100.0
        
        latest = self.metrics_history[-1]
        if 'error' in latest:
            return 0.0

        # Calculate health score using main metrics
        main_metrics = ['cpu_usage', 'memory_usage', 'disk_usage']
        values = [float(latest.get(metric, 0.0)) for metric in main_metrics]
        score = 100.0 - (sum(values) / len(values))
        
        return max(0.0, min(100.0, score))

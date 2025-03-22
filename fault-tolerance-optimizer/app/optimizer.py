class FaultToleranceOptimizer:
    def generate_recommendations(self, predictions, metrics):
        recommendations = []
        
        # CPU recommendations
        if metrics['cpu_usage'] > 90:
            recommendations.append("CRITICAL: CPU usage extremely high")
        elif metrics['cpu_usage'] > 80:
            recommendations.append("WARNING: CPU usage high")
            
        # Memory recommendations
        if metrics['memory_usage'] > 90:
            recommendations.append("CRITICAL: Memory usage extremely high")
        elif metrics['memory_usage'] > 80:
            recommendations.append("WARNING: Memory usage high")
            
        # Disk recommendations
        if metrics['disk_usage'] > 90:
            recommendations.append("CRITICAL: Disk usage extremely high")
        elif metrics['disk_usage'] > 80:
            recommendations.append("WARNING: Disk usage high")
            
        # Add prediction-based recommendations
        if predictions['failure_probability'] > 0.7:
            recommendations.append(f"CRITICAL: High failure probability detected! Time to failure: {predictions['estimated_time_to_failure']}")
            
        return recommendations if recommendations else ["System operating normally"]

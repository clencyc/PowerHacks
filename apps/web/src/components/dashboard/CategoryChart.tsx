import { Card } from "@/components/ui/card";
import { useEffect, useState } from "react";
import { API_BASE_URL, API_ENDPOINTS } from "@/lib/api";

const CategoryChart = () => {
  const [categories, setCategories] = useState([]);
  const [totalReports, setTotalReports] = useState(0);

  const categoryColors = {
    Harassment: "bg-primary",
    Discrimination: "bg-accent",
    "Verbal Abuse": "bg-orange-400",
    Bullying: "bg-pink-400",
  };

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.analytics}`);
        const data = await response.json();
        const categoryData = Object.entries(data.category_distribution).map(([name, count]) => ({
          name,
          count,
          percentage: (count / data.total_reports) * 100,
          color: categoryColors[name] || "bg-gray-400",
        }));
        setCategories(categoryData);
        setTotalReports(data.total_reports);
      } catch (error) {
        console.error("Error fetching chart data:", error);
      }
    };

    fetchChartData();
  }, []);

  return (
    <Card className="glass-card rounded-3xl p-6 h-full">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-foreground">Report Categories</h3>
        <p className="text-sm text-muted-foreground">Breakdown by type</p>
      </div>

      <div className="space-y-6">
        {categories.map((category) => (
          <div key={category.name}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-foreground">{category.name}</span>
              <span className="text-sm font-bold text-foreground">{category.count}</span>
            </div>
            <div className="w-full h-3 bg-white/50 rounded-full overflow-hidden">
              <div
                className={`h-full ${category.color} rounded-full transition-all duration-500`}
                style={{ width: `${category.percentage}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">{category.percentage.toFixed(0)}% of total</p>
          </div>
        ))}
      </div>

      <div className="mt-8 pt-6 border-t border-border/30">
        <div className="text-center">
          <p className="text-2xl font-bold text-foreground mb-1">
            {totalReports}
          </p>
          <p className="text-xs text-muted-foreground">Total Reports This Month</p>
        </div>
      </div>
    </Card>
  );
};

export default CategoryChart;
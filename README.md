# HEATWATCH: Historical Weather Trend & Extreme Temperature Analysis

## 1. Project Title
**HEATWATCH**: Historical Weather Trend & Extreme Temperature Analysis

## 2. Aim
To develop an interactive analytical dashboard that explores historical meteorological trends, identifies seasonal patterns, and detects unusual temperature events using statistical anomaly detection.

## 3. Problem Statement
Understanding how weather patterns change over time and identifying statistically unusual extreme temperature events is critical for climate intelligence. Without a clear analysis of historical baselines, it is difficult to determine whether a current weather observation is normal, unusual, or an extreme anomaly for a specific region and time of year.

## 4. Use-Case Alignment
This project acts as the Historical Data Analysis and Extreme Event Detection module for the HeatWatch use case. It strictly focuses on historical pattern analysis and mathematical anomaly detection, explicitly omitting predictive forecasting and official heatwave advisory generation.

## 5. Objectives
- Analyze long-term temperature and rainfall trends across multiple Indian cities.
- Break down weather observations into recurring seasonal patterns.
- Compare current or recent weather conditions against a historical baseline.
- Identify "unusual" and "extreme" temperature events using standard statistical methods (Z-scores).
- Provide a clear, non-technical, user-friendly interactive dashboard.

## 6. Dataset
We used a comprehensive daily weather dataset containing historical observations for multiple major Indian cities, covering the period from 2000 to 2024.

## 7. Methodology
The project employs a data-driven analytical approach. The dataset is parsed and grouped by city and time period. For extreme event detection, we calculate the historical mean and standard deviation for each specific city and month to form a reliable baseline, preventing unfair comparisons (e.g., comparing summer temperatures to winter averages).

## 8. Historical Analysis
This module visualizes the yearly average maximum and minimum temperatures, allowing users to observe warming or cooling trends over the past two decades.

## 9. Seasonal Analysis
Weather observations are aggregated into four distinct seasons (Summer, Monsoon, Post-Monsoon, Winter) to help users identify recurring cyclical patterns in temperature and rainfall for any selected region.

## 10. Live Analysis
The dashboard integrates with a public weather API (Open-Meteo) to fetch the current live temperature for a selected city. It then statistically compares this live observation against the historical baseline for the current month, instantly indicating whether today's weather is normal or anomalous.

## 11. Extreme Temperature Detection
We identify historical observations that deviate significantly from their expected norms. This is an analytical indicator and is not meant to replace official IMD heatwave severity classifications.

## 12. Z-score Method
We use the Z-score statistical method for anomaly detection:
`Z = (Actual Temperature - Historical Mean) / Historical Standard Deviation`
- **NORMAL**: |Z| < 2
- **UNUSUAL**: 2 ≤ |Z| < 3
- **EXTREME**: |Z| ≥ 3

## 13. Dashboard Modules
- **Tab 1: Historical Analysis**: Interactive trend lines, seasonal bar charts, and recent vs. historical comparative metrics.
- **Tab 2: Live Analysis**: Real-time telemetry compared against historical distributions with dynamic anomaly badges.
- **Tab 3: Extreme Events**: A deep dive into the top 10 most unusual temperature observations and an interactive timeline highlighting anomalies.

## 14. Results
The analysis successfully isolated historical temperature extremes, demonstrating that statistical z-scores applied on a per-city, per-month basis effectively identify genuine anomalies without triggering false positives during naturally hot summer months.

## 15. Limitations
- The Z-score method assumes a normal distribution of temperatures, which may not perfectly capture the complex long-tail distribution of climate data.
- The live analysis relies on a free, third-party weather API which may have slight discrepancies compared to local ground-station sensors.

## 16. Future Scope
- Integrating moving-window baselines (e.g., comparing today only to the last 5 years rather than the last 20 years) to account for shifting climate normals.
- Adding geospatial mapping (heatmaps) to visualize extreme events across the country simultaneously.

## 17. Installation
Install the required dependencies using:
```bash
pip install -r requirements.txt
```

## 18. Run Instructions
To start the interactive dashboard, run:
```bash
streamlit run app.py
```

## 19. Viva Questions

**Q: What is your project?**
A: "Our project is a Historical Weather Trend and Extreme Temperature Analysis module for HeatWatch. It analyzes historical meteorological observations, identifies temperature trends and seasonal patterns, and detects unusually high or low temperature observations."

**Q: Why did you choose this module?**
A: "The HeatWatch use case includes historical meteorological analysis and region-wise and seasonal analysis. We implemented this functionality as an interactive dashboard."

**Q: What dataset did you use?**
A: "We used a daily weather dataset containing historical observations for multiple Indian cities."

**Q: What is anomaly detection here?**
A: "We compare a temperature observation with its historical pattern for that city and period. If it is significantly different, we flag it as unusual or extreme."

**Q: Which algorithm did you use?**
A: "For extreme-event detection we use a statistical Z-score method because it is simple, interpretable and suitable for identifying observations that deviate significantly from the historical pattern."

**Q: Is this official IMD heatwave classification?**
A: "No. Our anomaly status is an analytical indicator based on historical statistics. It is not an official IMD heatwave warning."

**Q: Where does live data come from?**
A: "For the prototype, live observations are obtained from a weather API. In the complete HeatWatch architecture, this observation layer can be supplied by the AWS infrastructure described in the use case."

**Q: Are you doing forecasting?**
A: "No. Forecasting is outside our selected module. Our module focuses on historical analysis and unusual/extreme temperature observations."

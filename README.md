# BI Architect - Executive Dashboard

A sophisticated Business Intelligence system that serves non-technical executives through natural language queries. This application uses the structured BI Architect system prompt to ensure high accuracy and valid outputs.

## Features

- **Natural Language Interface**: Executives can ask questions in plain English
- **AI-Powered Analysis**: Uses Gemini AI with structured system prompt for accuracy
- **Automatic Visualization**: Intelligently selects appropriate chart types
- **SQL Generation**: Converts natural language to valid SQL queries
- **Interactive Dashboard**: Modern, responsive web interface
- **Real-time Results**: Instant data visualization and analysis

## Architecture

### System Prompt Design
The application uses a carefully crafted system prompt that forces the LLM to act as a structured architect:

- **Role Definition**: Expert Data Scientist and BI Architect
- **Clear Task Structure**: 4-step process with specific requirements
- **Schema Context**: Pre-defined database schema with sales data
- **Strict JSON Output**: Enforced response format for consistency
- **Constraint Rules**: Business logic for chart selection and SQL generation

### Database Schema
```sql
sales_data (
    date DATE,
    region TEXT,
    category TEXT,
    product_name TEXT,
    revenue FLOAT,
    units_sold INT
)
```

## Installation

1. **Clone and Setup**:
   ```bash
   cd bi-architect
   pip install -r requirements.txt
   ```

2. **Set up Gemini API Key**:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   Or set it in your environment variables.

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Dashboard**:
   Open http://localhost:5000 in your browser

## Usage

### For Non-Technical Executives

Simply type your business questions in natural language:

- "Show me revenue by region for the last month"
- "What are the top 5 products by sales?"
- "Compare revenue across categories"
- "Show monthly sales trend"

The system will:
1. Analyze your request
2. Generate appropriate SQL query
3. Execute the query against the database
4. Select the best visualization type
5. Display results with analysis

### Sample Query Types

| Query Type | Example | Chart Type | Use Case |
|------------|---------|------------|----------|
| Time Series | "Show monthly sales trend" | Line/Area | Tracking trends over time |
| Comparison | "Compare revenue across regions" | Bar | Comparing categories |
| Part-to-Whole | "Show revenue share by category" | Pie | Understanding proportions |
| Ranking | "Top 10 products by revenue" | Bar | Performance analysis |

## Technical Implementation

### Key Components

1. **System Prompt Engine**: Enforces structured LLM responses
2. **SQL Generator**: Converts natural language to valid SQL
3. **Visualization Engine**: Automatic chart type selection
4. **Error Handling**: Graceful failure management
5. **Data Pipeline**: End-to-end query processing

### Chart Selection Logic

- **Time-series data**: Line or Area charts
- **Part-to-whole relationships**: Pie charts
- **Comparisons**: Bar charts
- **Correlations**: Scatter plots

### SQL Generation Rules

- Uses only schema-defined columns
- Implements proper GROUP BY and ORDER BY
- Ensures query validity and performance
- Handles aggregations and filtering

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key

### Database
- Uses SQLite for simplicity
- Auto-generates sample data on first run
- 6 months of historical sales data
- 1000+ sample records across regions and categories

## Sample Data

The system comes pre-loaded with sample sales data including:
- 5 geographic regions (North, South, East, West, Central)
- 5 product categories (Electronics, Clothing, Food, Books, Sports)
- 6 months of historical data
- Realistic revenue and unit sales figures

## Error Handling

The system includes comprehensive error handling:
- Invalid SQL queries
- API key issues
- Malformed LLM responses
- Database connection problems
- Chart generation failures

## Security Considerations

- SQL injection protection through parameterized queries
- API key security through environment variables
- Input validation and sanitization
- Error message sanitization

## Future Enhancements

- Multiple database support (PostgreSQL, MySQL)
- Additional chart types and customization
- Export functionality (PDF, Excel)
- User authentication and permissions
- Real-time data streaming
- Advanced analytics and forecasting

## Support

For issues or questions:
1. Check the error messages in the dashboard
2. Verify API key configuration
3. Ensure database connectivity
4. Review query syntax for complex requests

This system is designed specifically for non-technical executives to access business intelligence without requiring technical expertise or SQL knowledge.

# analytics.py
import pandas as pd
import plotly.express as px


class ExpenseAnalytics:
    """Analytics class for expense data visualization and calculations"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if not df.empty:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['month'] = self.df['date'].dt.to_period('M')
            self.df['week'] = self.df['date'].dt.to_period('W')

    def get_category_spending(self) -> pd.DataFrame:
        """Get spending by category"""
        if self.df.empty:
            return pd.DataFrame()
        return self.df.groupby('category')['amount'].sum().reset_index()

    def get_monthly_spending(self) -> pd.DataFrame:
        """Get monthly spending trends"""
        if self.df.empty:
            return pd.DataFrame()
        monthly_data = self.df.groupby('month')['amount'].sum().reset_index()
        monthly_data['month_str'] = monthly_data['month'].astype(str)
        return monthly_data

    def get_daily_spending(self) -> pd.DataFrame:
        """Get daily spending trends"""
        if self.df.empty:
            return pd.DataFrame()
        return self.df.groupby('date')['amount'].sum().reset_index()

    def get_top_categories(self, n: int = 5) -> pd.DataFrame:
        """Get top N spending categories"""
        category_spending = self.get_category_spending()
        if category_spending.empty:
            return pd.DataFrame()
        return category_spending.nlargest(n, 'amount')

    def create_category_pie_chart(self):
        """Create pie chart for category spending"""
        category_data = self.get_category_spending()
        if category_data.empty:
            return None

        fig = px.pie(
            category_data,
            values='amount',
            names='category',
            title="<b>Spending Distribution by Category</b>",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12,
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            font=dict(size=12),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle",
                        y=0.5, xanchor="left", x=1.05),
            margin=dict(t=50, b=30, l=30, r=150)
        )

        return fig

    def create_monthly_bar_chart(self):
        """Create bar chart for monthly spending"""
        monthly_data = self.get_monthly_spending()
        if monthly_data.empty:
            return None

        fig = px.bar(
            monthly_data,
            x='month_str',
            y='amount',
            title="<b>Monthly Spending Trends</b>",
            color='amount',
            color_continuous_scale='viridis',
            text='amount'
        )

        fig.update_traces(
            texttemplate='₹%{text:,.0f}',
            textposition='outside',
            marker_line_width=1,
            marker_line_color='white'
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            xaxis_title="<b>Month</b>",
            yaxis_title="<b>Amount (₹)</b>",
            font=dict(size=12),
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50)
        )

        return fig

    def create_daily_line_chart(self):
        """Create line chart for daily spending trends"""
        daily_data = self.get_daily_spending()
        if daily_data.empty:
            return None

        fig = px.line(
            daily_data,
            x='date',
            y='amount',
            title="<b>Daily Spending Trends</b>",
            markers=True,
            line_shape='spline'
        )

        fig.update_traces(
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#764ba2',
                        line=dict(width=2, color='white'))
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            xaxis_title="<b>Date</b>",
            yaxis_title="<b>Amount (₹)</b>",
            font=dict(size=12),
            hovermode='x unified',
            margin=dict(t=50, b=50, l=50, r=50)
        )

        return fig

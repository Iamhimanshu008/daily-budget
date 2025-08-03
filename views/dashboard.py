# pages/dashboard.py
import streamlit as st
from database import ExpenseTrackerDB
from analytics import ExpenseAnalytics


def show_dashboard(db: ExpenseTrackerDB):
    """Display comprehensive analytics dashboard"""
    st.markdown('<h2><i class="fas fa-chart-line icon"></i>Analytics Dashboard</h2>',
                unsafe_allow_html=True)

    # Get user expenses
    expenses_df = db.get_expenses(st.session_state.user['id'])

    if expenses_df.empty:
        st.markdown('''
        <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 15px; margin: 2rem 0;">
            <i class="fas fa-chart-bar" style="font-size: 4rem; color: #9ca3af; margin-bottom: 1rem;"></i>
            <h3 style="color: #6b7280;">No Data Available</h3>
            <p style="color: #9ca3af; margin-bottom: 2rem;">Start tracking your expenses to see analytics and insights here.</p>
        </div>
        ''', unsafe_allow_html=True)

        if st.button("Add Your First Expense", type="primary", use_container_width=True):
            st.session_state.current_page = 'add_expense'
            st.rerun()
        return

    # Initialize analytics
    analytics = ExpenseAnalytics(expenses_df)

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    total_expenses = expenses_df['amount'].sum()
    avg_expense = expenses_df['amount'].mean()
    expense_count = len(expenses_df)
    top_category = analytics.get_top_categories(1)
    top_cat_name = top_category['category'].iloc[0] if not top_category.empty else "N/A"

    with col1:
        st.metric(
            label="💰 Total Spent",
            value=f"₹{total_expenses:,.2f}",
            help="Total amount spent across all categories"
        )
    with col2:
        st.metric(
            label="📊 Average Expense",
            value=f"₹{avg_expense:.2f}",
            help="Average amount per expense entry"
        )
    with col3:
        st.metric(
            label="📋 Total Records",
            value=f"{expense_count}",
            help="Total number of expense entries"
        )
    with col4:
        st.metric(
            label="🏆 Top Category",
            value=top_cat_name,
            help="Category with highest spending"
        )

    st.markdown("---")

    # Charts section
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        pie_chart = analytics.create_category_pie_chart()
        if pie_chart:
            st.plotly_chart(pie_chart, use_container_width=True)

    with chart_col2:
        bar_chart = analytics.create_monthly_bar_chart()
        if bar_chart:
            st.plotly_chart(bar_chart, use_container_width=True)

    # Daily trends (full width)
    line_chart = analytics.create_daily_line_chart()
    if line_chart:
        st.plotly_chart(line_chart, use_container_width=True)

    # Recent expenses section
    st.markdown('<h3><i class="fas fa-clock icon"></i>Recent Expenses</h3>',
                unsafe_allow_html=True)

    recent_expenses = expenses_df.head(5)
    for _, expense in recent_expenses.iterrows():
        st.markdown(f'''
        <div class="expense-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="font-size: 1.1rem; color: #1f2937;">₹{expense['amount']:.2f}</strong>
                    <span style="margin-left: 1rem; color: #6b7280;">→ {expense['category']}</span>
                </div>
                <div style="text-align: right; color: #9ca3af; font-size: 0.9rem;">
                    {expense['date']}
                </div>
            </div>
            <div style="margin-top: 0.5rem; color: #6b7280; font-size: 0.9rem;">
                <i class="fas fa-comment-alt" style="margin-right: 0.5rem;"></i>
                {expense['description'] if expense['description'] else 'No description'}
            </div>
        </div>
        ''', unsafe_allow_html=True)

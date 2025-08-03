# pages/budget.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database import ExpenseTrackerDB


def show_budget_tracker(db: ExpenseTrackerDB):
    """Display comprehensive budget tracking interface"""
    st.markdown('<h2><i class="fas fa-bullseye icon"></i>Budget Tracker</h2>',
                unsafe_allow_html=True)

    # Current month/year selection
    current_date = datetime.now()

    budget_col1, budget_col2 = st.columns(2)

    with budget_col1:
        selected_month = st.selectbox(
            "📅 Select Month",
            options=list(range(1, 13)),
            index=current_date.month - 1,
            format_func=lambda x: datetime(2024, x, 1).strftime('%B')
        )

    with budget_col2:
        selected_year = st.selectbox(
            "📅 Select Year",
            options=list(range(current_date.year - 2, current_date.year + 2)),
            index=2  # Current year
        )

    st.markdown("---")

    # Budget setting section
    st.markdown('<h3><i class="fas fa-cog icon"></i>Set Monthly Budgets</h3>',
                unsafe_allow_html=True)

    categories = [
        ("Food & Dining", "fas fa-utensils"),
        ("Transportation", "fas fa-car"),
        ("Housing", "fas fa-home"),
        ("Shopping", "fas fa-shopping-bag"),
        ("Healthcare", "fas fa-heartbeat"),
        ("Entertainment", "fas fa-film"),
        ("Education", "fas fa-graduation-cap"),
        ("Business", "fas fa-briefcase"),
        ("Travel", "fas fa-plane"),
        ("Utilities", "fas fa-bolt"),
        ("Clothing", "fas fa-tshirt"),
        ("Gifts", "fas fa-gift"),
        ("Other", "fas fa-ellipsis-h")
    ]

    with st.form("budget_form"):
        budget_form_col1, budget_form_col2, budget_form_col3 = st.columns(3)

        with budget_form_col1:
            budget_category = st.selectbox(
                "📂 Category",
                options=[cat[0] for cat in categories]
            )

        with budget_form_col2:
            budget_amount = st.number_input(
                "💰 Monthly Budget (₹)",
                min_value=0.01,
                step=1.00,
                format="%.2f"
            )

        with budget_form_col3:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.form_submit_button("💾 Set Budget", type="primary", use_container_width=True):
                if budget_amount > 0:
                    if db.set_budget(st.session_state.user['id'], budget_category, budget_amount, selected_month,
                                     selected_year):
                        st.success(
                            f"Budget set for {budget_category}: ₹{budget_amount:.2f}")
                        st.rerun()
                    else:
                        st.error("Failed to set budget.")
                else:
                    st.warning("Please enter a valid budget amount.")

    st.markdown("---")

    # Budget vs Actual Analysis
    st.markdown(
        f'<h3><i class="fas fa-chart-bar icon"></i>Budget Analysis - {datetime(selected_year, selected_month, 1).strftime("%B %Y")}</h3>',
        unsafe_allow_html=True)

    # Get budgets and expenses for selected month/year
    budgets_df = db.get_budgets(
        st.session_state.user['id'], selected_month, selected_year)
    expenses_df = db.get_expenses(st.session_state.user['id'])

    if budgets_df.empty:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 10px;">
            <i class="fas fa-chart-pie" style="font-size: 3rem; color: #9ca3af; margin-bottom: 1rem;"></i>
            <h4 style="color: #6b7280;">No Budgets Set</h4>
            <p style="color: #9ca3af;">Set budgets for different categories to track your spending.</p>
        </div>
        ''', unsafe_allow_html=True)
        return

    if not expenses_df.empty:
        # Filter expenses for selected month/year
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        current_month_expenses = expenses_df[
            (expenses_df['date'].dt.month == selected_month) &
            (expenses_df['date'].dt.year == selected_year)
        ]

        # Calculate actual spending by category
        if not current_month_expenses.empty:
            actual_spending = current_month_expenses.groupby(
                'category')['amount'].sum().reset_index()
            actual_spending.columns = ['category', 'actual_amount']
        else:
            actual_spending = pd.DataFrame(
                columns=['category', 'actual_amount'])

        # Merge budgets with actual spending
        budget_analysis = budgets_df.merge(
            actual_spending,
            on='category',
            how='left'
        )
        budget_analysis['actual_amount'] = budget_analysis['actual_amount'].fillna(
            0)
        budget_analysis['remaining'] = budget_analysis['amount'] - \
            budget_analysis['actual_amount']
        budget_analysis['percentage'] = (
            budget_analysis['actual_amount'] / budget_analysis['amount'] * 100).round(1)

        # Summary metrics
        total_budget = budget_analysis['amount'].sum()
        total_spent = budget_analysis['actual_amount'].sum()
        total_remaining = budget_analysis['remaining'].sum()
        overall_percentage = (total_spent / total_budget *
                              100) if total_budget > 0 else 0

        # Display summary cards
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        with summary_col1:
            st.metric("💰 Total Budget", f"₹{total_budget:,.2f}")
        with summary_col2:
            st.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
        with summary_col3:
            st.metric("💵 Remaining", f"₹{total_remaining:,.2f}")
        with summary_col4:
            st.metric("📊 Used", f"{overall_percentage:.1f}%")

        st.markdown("---")

        # Individual category analysis
        for _, row in budget_analysis.iterrows():
            percentage = row['percentage']

            # Determine status and styling
            if percentage > 100:
                status_class = "budget-danger"
                status_text = "🚨 Over Budget!"
                progress_class = "progress-danger"
                # Cap at 150% for display
                progress_width = min(percentage, 150)
            elif percentage > 80:
                status_class = "budget-warning"
                status_text = "⚠️ Near Limit"
                progress_class = "progress-warning"
                progress_width = percentage
            else:
                status_class = "budget-success"
                status_text = "✅ On Track"
                progress_class = "progress-success"
                progress_width = percentage

            st.markdown(f'''
            <div class="{status_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0;"><i class="fas fa-tag icon"></i>{row['category']}</h4>
                    <span style="font-weight: bold; font-size: 1.1rem;">{status_text}</span>
                </div>

                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span><strong>Budget:</strong> ₹{row['amount']:,.2f}</span>
                    <span><strong>Spent:</strong> ₹{row['actual_amount']:,.2f}</span>
                    <span><strong>Remaining:</strong> ₹{row['remaining']:,.2f}</span>
                </div>

                <div class="progress-container">
                    <div class="progress-bar {progress_class}" style="width: {progress_width}%;"></div>
                </div>

                <div style="text-align: center; font-size: 0.9rem; margin-top: 0.5rem;">
                    <strong>{percentage:.1f}%</strong> of budget used
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # Budget insights
        st.markdown("---")
        st.markdown(
            '<h4><i class="fas fa-lightbulb icon"></i>Budget Insights</h4>', unsafe_allow_html=True)

        over_budget_categories = budget_analysis[budget_analysis['percentage'] > 100]
        near_limit_categories = budget_analysis[(
            budget_analysis['percentage'] > 80) & (
            budget_analysis['percentage'] <= 100)]
        under_budget_categories = budget_analysis[budget_analysis['percentage'] <= 50]

        insights_col1, insights_col2 = st.columns(2)

        with insights_col1:
            if not over_budget_categories.empty:
                st.markdown(f'''
                <div class="alert-error">
                    <h5><i class="fas fa-exclamation-triangle icon"></i>Over Budget ({len(over_budget_categories)} categories)</h5>
                    <ul style="margin: 0;">
                        {"".join([f"<li>{row['category']}: {row['percentage']:.1f}% used</li>" for _, row in over_budget_categories.iterrows()])}
                    </ul>
                </div>
                ''', unsafe_allow_html=True)

            if not near_limit_categories.empty:
                st.markdown(f'''
                <div class="alert-warning">
                    <h5><i class="fas fa-exclamation-circle icon"></i>Near Limit ({len(near_limit_categories)} categories)</h5>
                    <ul style="margin: 0;">
                        {"".join([f"<li>{row['category']}: {row['percentage']:.1f}% used</li>" for _, row in near_limit_categories.iterrows()])}
                    </ul>
                </div>
                ''', unsafe_allow_html=True)

        with insights_col2:
            if not under_budget_categories.empty:
                st.markdown(f'''
                <div class="alert-success">
                    <h5><i class="fas fa-check-circle icon"></i>Well Under Budget ({len(under_budget_categories)} categories)</h5>
                    <ul style="margin: 0;">
                        {"".join([f"<li>{row['category']}: {row['percentage']:.1f}% used</li>" for _, row in under_budget_categories.iterrows()])}
                    </ul>
                </div>
                ''', unsafe_allow_html=True)

            # Recommendations
            if total_remaining > 0:
                st.markdown(f'''
                <div style="background: #e0f2fe; border-left: 4px solid #0288d1; padding: 1rem; border-radius: 8px;">
                    <h5><i class="fas fa-info-circle icon"></i>Savings Opportunity</h5>
                    <p style="margin: 0;">You have <strong>₹{total_remaining:,.2f}</strong> remaining across all budgets. Consider saving or investing this amount!</p>
                </div>
                ''', unsafe_allow_html=True)

    else:
        st.info("No expenses recorded for the selected period.")

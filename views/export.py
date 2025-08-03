# pages/export.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database import ExpenseTrackerDB
from analytics import ExpenseAnalytics


def show_export_data(db: ExpenseTrackerDB):
    """Display comprehensive data export interface"""
    st.markdown('<h2><i class="fas fa-download icon"></i>Export Your Data</h2>',
                unsafe_allow_html=True)

    expenses_df = db.get_expenses(st.session_state.user['id'])

    if expenses_df.empty:
        st.markdown('''
        <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 15px;">
            <i class="fas fa-file-export" style="font-size: 4rem; color: #9ca3af; margin-bottom: 1rem;"></i>
            <h3 style="color: #6b7280;">No Data to Export</h3>
            <p style="color: #9ca3af;">Add some expenses first to export your data.</p>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Data summary
    export_col1, export_col2 = st.columns(2)

    with export_col1:
        st.markdown(
            '<h3><i class="fas fa-chart-bar icon"></i>Export Summary</h3>', unsafe_allow_html=True)

        total_expenses = len(expenses_df)
        total_amount = expenses_df['amount'].sum()
        avg_amount = expenses_df['amount'].mean()
        date_range = f"{expenses_df['date'].min()} to {expenses_df['date'].max()}"
        categories_count = expenses_df['category'].nunique()

        st.markdown(f'''
        <div class="metric-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-list icon"></i><strong>Total Records:</strong> {total_expenses}</p>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-dollar-sign icon"></i><strong>Total Amount:</strong> ₹{total_amount:,.2f}</p>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-chart-line icon"></i><strong>Average:</strong> ₹{avg_amount:.2f}</p>
                </div>
                <div>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-calendar icon"></i><strong>Date Range:</strong></p>
                    <p style="margin: 0 0 0.25rem 1.5rem; font-size: 0.9rem;">{date_range}</p>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-tags icon"></i><strong>Categories:</strong> {categories_count}</p>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with export_col2:
        st.markdown(
            '<h3><i class="fas fa-cog icon"></i>Export Options</h3>', unsafe_allow_html=True)

        # Export filters
        with st.form("export_filters"):
            st.markdown('<h5>Filter Data Before Export</h5>',
                        unsafe_allow_html=True)

            # Date range filter
            min_date = pd.to_datetime(expenses_df['date']).min().date()
            max_date = pd.to_datetime(expenses_df['date']).max().date()

            export_date_range = st.date_input(
                "📅 Date Range",
                value=(min_date, max_date),
                key="export_date_filter"
            )

            # Category filter
            all_categories = ['All Categories'] + \
                sorted(expenses_df['category'].unique().tolist())
            export_categories = st.multiselect(
                "📂 Categories",
                options=all_categories[1:],  # Exclude 'All Categories'
                default=all_categories[1:]   # Select all by default
            )

            # Amount range filter
            min_amount = float(expenses_df['amount'].min())
            max_amount = float(expenses_df['amount'].max())
            export_amount_range = st.slider(
                "💰 Amount Range",
                min_value=min_amount,
                max_value=max_amount,
                value=(min_amount, max_amount),
                step=0.01
            )

            apply_filters = st.form_submit_button(
                "🔄 Apply Filters", type="secondary")

    # Apply export filters
    export_df = expenses_df.copy()
    export_df['date'] = pd.to_datetime(export_df['date'])

    if len(export_date_range) == 2:
        start_date, end_date = export_date_range
        export_df = export_df[
            (export_df['date'].dt.date >= start_date) &
            (export_df['date'].dt.date <= end_date)
        ]

    if export_categories:
        export_df = export_df[export_df['category'].isin(export_categories)]

    export_df = export_df[
        (export_df['amount'] >= export_amount_range[0]) &
        (export_df['amount'] <= export_amount_range[1])
    ]

    # Show filtered results
    filtered_count = len(export_df)
    filtered_total = export_df['amount'].sum()

    if filtered_count != total_expenses:
        st.markdown(f'''
        <div class="alert-warning">
            <i class="fas fa-filter icon"></i>
            <strong>Filtered Results:</strong> {filtered_count} records (₹{filtered_total:,.2f}) will be exported
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Download section
    st.markdown('<h3><i class="fas fa-file-download icon"></i>Download Files</h3>',
                unsafe_allow_html=True)

    download_col1, download_col2, download_col3 = st.columns(3)

    # Prepare data for export
    export_data = export_df.copy()
    export_data['date'] = export_data['date'].dt.strftime('%Y-%m-%d')

    with download_col1:
        # CSV Export
        csv_data = export_data.to_csv(index=False)
        filename_base = f"expenses_{st.session_state.user['username']}_{datetime.now().strftime('%Y%m%d')}"

        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"{filename_base}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Comma-separated values file, compatible with Excel and Google Sheets"
        )

    with download_col2:
        # JSON Export
        json_data = export_data.to_json(
            orient='records', date_format='iso', indent=2)

        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name=f"{filename_base}.json",
            mime="application/json",
            use_container_width=True,
            help="JavaScript Object Notation format, good for developers"
        )

    with download_col3:
        # Excel Export (using pandas to_excel would require openpyxl, so we'll use CSV with .xlsx extension as fallback)
        st.download_button(
            label="📊 Download Excel*",
            data=csv_data,
            file_name=f"{filename_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="*Note: This downloads as CSV format with .xlsx extension. Open with Excel for best results."
        )

    # Advanced export options
    st.markdown("---")
    st.markdown('<h4><i class="fas fa-tools icon"></i>Advanced Export Options</h4>',
                unsafe_allow_html=True)

    advanced_col1, advanced_col2 = st.columns(2)

    with advanced_col1:
        # Summary report
        if st.button("📈 Generate Summary Report", use_container_width=True):
            analytics = ExpenseAnalytics(export_df)
            category_summary = analytics.get_category_spending()
            monthly_summary = analytics.get_monthly_spending()

            # Create detailed summary
            summary_report = f"""
EXPENSE SUMMARY REPORT
======================

Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
User: {st.session_state.user['username']}
Period: {export_date_range[0] if len(export_date_range) == 2 else 'All'} to {export_date_range[1] if len(export_date_range) == 2 else 'All'}

OVERVIEW
--------
Total Expenses: {len(export_df)}
Total Amount: ₹{export_df['amount'].sum():,.2f}
Average Amount: ₹{export_df['amount'].mean():.2f}
Median Amount: ₹{export_df['amount'].median():.2f}

SPENDING BY CATEGORY
-------------------
"""

            for _, row in category_summary.iterrows():
                percentage = (row['amount'] / export_df['amount'].sum()) * 100
                summary_report += f"{row['category']}: ₹{row['amount']:,.2f} ({percentage:.1f}%)\n"

            summary_report += f"""

MONTHLY BREAKDOWN
----------------
"""

            for _, row in monthly_summary.iterrows():
                summary_report += f"{row['month']}: ₹{row['amount']:,.2f}\n"

            st.download_button(
                label="📄 Download Summary Report",
                data=summary_report,
                file_name=f"summary_{filename_base}.txt",
                mime="text/plain",
                use_container_width=True
            )

    with advanced_col2:
        # Category breakdown
        if st.button("📊 Export Category Breakdown", use_container_width=True):
            analytics = ExpenseAnalytics(export_df)
            category_data = analytics.get_category_spending()

            if not category_data.empty:
                category_csv = category_data.to_csv(index=False)
                st.download_button(
                    label="📄 Download Category Data",
                    data=category_csv,
                    file_name=f"categories_{filename_base}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # Data preview
    st.markdown("---")
    st.markdown('<h4><i class="fas fa-eye icon"></i>Data Preview</h4>',
                unsafe_allow_html=True)

    if not export_df.empty:
        # Show first few rows
        preview_data = export_df.head(10).copy()
        preview_data['date'] = preview_data['date'].dt.strftime('%Y-%m-%d')

        st.dataframe(
            preview_data[['date', 'category', 'amount', 'description']],
            use_container_width=True,
            hide_index=True
        )

        if len(export_df) > 10:
            st.info(
                f"Showing first 10 of {len(export_df)} records. Download files to see all data.")
    else:
        st.warning("No data matches the current filters.")

    # Export tips
    st.markdown("---")
    st.markdown('<h4><i class="fas fa-lightbulb icon"></i>Export Tips</h4>',
                unsafe_allow_html=True)

    tips_col1, tips_col2 = st.columns(2)

    with tips_col1:
        st.markdown('''
        <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3;">
            <h5><i class="fas fa-file-csv icon"></i>CSV Files</h5>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Best for Excel and Google Sheets</li>
                <li>Universal compatibility</li>
                <li>Smallest file size</li>
                <li>Easy to import into other tools</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

    with tips_col2:
        st.markdown('''
        <div style="background: #f3e5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid #9c27b0;">
            <h5><i class="fas fa-code icon"></i>JSON Files</h5>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Perfect for developers</li>
                <li>Structured data format</li>
                <li>Easy to parse programmatically</li>
                <li>Preserves data types</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

    # Privacy notice
    st.markdown("---")
    st.markdown('''
    <div style="background: #fff3e0; border: 1px solid #ff9800; padding: 1rem; border-radius: 8px;">
        <h5><i class="fas fa-shield-alt icon"></i>Privacy & Security</h5>
        <p style="margin: 0;">Your data is exported directly from your browser. No data is sent to external servers during export. Keep your exported files secure and only share them with trusted parties.</p>
    </div>
    ''', unsafe_allow_html=True)

import os

import streamlit as st
from sqlalchemy import Engine, create_engine, text
import pandas as pd
from dotenv import load_dotenv


class App:
    """Streamlit Jobs Hunting app"""

    def __init__(self):
        # Set page view
        st.set_page_config(layout="wide")
        st.sidebar.title(":rainbow-background[JOBS Hunting :rocket:]")

        # User input for keywords to include and exclude in title column
        inc_words = st.sidebar.text_input(
            "Keywords to include in Role",
            help=r"Many keywords can be inserted separated by commas. Leading and trailing spaces will be removed. The filter is case insensitive.",
        )
        exc_words = st.sidebar.text_input(
            "Keywords to exclude in Role",
            help=r"Many keywords can be inserted separated by commas. Leading and trailing spaces will be removed. The filter is case insensitive.",
        )
        # Strip any leading/trailing whitespace from keywords
        self.inc_words = [w.strip() for w in inc_words.split(",")]
        self.exc_words = [w.strip() for w in exc_words.split(",")]

        # Setup database
        self.engine = self.setup_db()

        # Fetch all data
        self.df = self.fetch_data()

        # Save a copy of the data
        self.original_df = self.df.copy()

        # Filter data before displaying it
        filtered_df = self.filter_data(self.df)

        # Hide viewed offers
        hide_viewed_offers = st.sidebar.checkbox("Hide viewed offers.")
        if hide_viewed_offers:
            filtered_df = filtered_df.query("viewed == False")
        # Display the number of rows retrieved
        st.sidebar.markdown(
            f"Found <b>{len(filtered_df)}</b> out of {len(self.original_df)} jobs.",
            unsafe_allow_html=True,
        )

        # Display the filtered data
        self.display_table(filtered_df)

    @st.cache_resource
    def setup_db(_self) -> Engine:
        """Connect to the database"""
        # Load environment variables
        load_dotenv()

        # Database URL
        PSQL_USER = os.getenv("PSQL_USER")
        PSQL_PASSWORD = os.getenv("PSQL_PASSWORD")
        PSQL_HOST = os.getenv("PSQL_HOST")
        PSQL_DB = os.getenv("PSQL_DB")

        DB_URL = f"postgresql://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:5432/{PSQL_DB}"

        # Create engine
        return create_engine(DB_URL)

    # Fetch all data
    def fetch_data(self) -> pd.DataFrame:
        """Fetch all data from the database"""
        query = """
            SELECT *  FROM jobs 
            WHERE added_at = (SELECT MAX(added_at) FROM jobs)
            ORDER BY posted_at DESC, id;"""  # Order by ID to ensure order consistency in equal dates
        return pd.read_sql(query, self.engine)

    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter the DataFrame based on include and exclude keywords"""

        # If both fields are empty, return the full dataset
        if not any(self.inc_words) and not any(self.exc_words):
            return df

        # Apply inclusion filter
        if any(self.inc_words):
            df = df[df["title"].str.contains("|".join(self.inc_words), case=False)]

        # Apply exclusion filter
        if any(self.exc_words):
            df = df[~df["title"].str.contains("|".join(self.exc_words), case=False)]

        return df

    def update_db(self, id: int, viewed: bool) -> None:
        """Update the `viewed` column in the database for a given ID"""
        with self.engine.begin() as conn:
            conn.execute(
                text("UPDATE jobs SET viewed = :status WHERE id = :id"),
                {"status": viewed, "id": id},
            )

    def style_table(self, df: pd.DataFrame):
        """Style the table. Capitalize column names and color code based on `viewed` column."""
        df.columns = [c.capitalize() for c in df.columns]
        return df.style.apply(
            lambda row: (
                ["background-color: #EF7171; color: black"] * len(row)
                if row["Viewed"]
                else ["background-color: #71EF86; color: black"] * len(row)
            ),
            axis=1,
        )

    def display_table(self, df: pd.DataFrame):
        """Display the table in **Streamlit**"""
        edited_df = st.data_editor(
            self.style_table(df),
            column_config={
                "Viewed": st.column_config.CheckboxColumn(label="", width=50),
                "Title": st.column_config.TextColumn(label="Role", width=300),
                "Company": st.column_config.TextColumn(width=200),
                "Location": st.column_config.TextColumn(width=200),
                "Url": st.column_config.LinkColumn(
                    "Link", width=150, display_text=r"https://(.*?)/.*"
                ),
            },
            column_order=["Viewed", "Url", "Title", "Company", "Location", "Posted_at"],
            disabled=[
                "Title",
                "Company",
                "Location",
                "Posted_at",
                "Url",
            ],
            height=500,
            hide_index=True,
        )

        # Compare changes and auto-save only modified rows
        for _, row in edited_df.iterrows():
            original_row = self.original_df[self.original_df["id"] == row["Id"]]
            if (
                not original_row.empty
                and row["Viewed"] != original_row.iloc[0]["viewed"]
            ):
                self.update_db(row["Id"], row["Viewed"])
                st.rerun()


if __name__ == "__main__":
    App()

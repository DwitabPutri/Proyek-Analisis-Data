import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Bike Sharing Data")

daily_hours_df = pd.read_csv('dashboard/daily_hours_df.csv')
hours_df = pd.read_csv('dashboard/hours_df.csv')
day_type_hours_df = pd.read_csv('dashboard/day_type_hours_df.csv')
cust_type_df = pd.read_csv('dashboard/cust_type_df.csv')

hours_df['yr'] = hours_df['yr'].map({0: 2011, 1: 2012})
daily_hours_df['dteday'] = pd.to_datetime(daily_hours_df['dteday'])

selected_dates = st.sidebar.date_input(
    "Select Date Range", 
    value=[daily_hours_df['dteday'].min().date(), daily_hours_df['dteday'].max().date()],
    key='date_range'
)

selected_hour = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))
selected_dates = pd.to_datetime(selected_dates)

filtered_daily_df = daily_hours_df[
    (daily_hours_df['dteday'] >= selected_dates[0]) & 
    (daily_hours_df['dteday'] <= selected_dates[1]) & 
    (daily_hours_df['hour'] >= selected_hour[0]) & 
    (daily_hours_df['hour'] <= selected_hour[1])
]

weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_mapping = {
    0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}

filtered_daily_df['weekday'] = pd.Categorical(filtered_daily_df['weekday'], categories=weekday_order, ordered=True)

col1, col2 = st.columns(2)

with col1:
    daily_sum = filtered_daily_df.groupby('weekday', observed=False)['sum_cnt'].sum().reindex(weekday_order)
    byweekday_df = pd.DataFrame({"weekday": weekday_order, "rental_count": daily_sum.values})

    plt.figure(figsize=(8, 6))
    sns.barplot(
        y="rental_count",
        x="weekday",
        hue="weekday",
        data=byweekday_df.sort_values(by="rental_count", ascending=False),
        palette="Blues_r",
        legend=False
    )
    plt.title("Total Bicycle Rentals by Day", loc="center", fontsize=15)
    plt.ylabel("Total Rentals", fontsize=12)
    plt.xlabel("Day", fontsize=12)
    plt.tight_layout()
    st.pyplot(plt.gcf())

with col2:
    hourly_sum = filtered_daily_df.groupby('hour', observed=False)['sum_cnt'].sum()
    byhour_df = pd.DataFrame({"hour": hourly_sum.index, "rental_count": hourly_sum.values})
    byhour_df = byhour_df.sort_values(by="hour", ascending=True)

    norm = plt.Normalize(byhour_df['rental_count'].min(), byhour_df['rental_count'].max())
    colors_list = [plt.cm.Blues(norm(value)) for value in byhour_df['rental_count']]

    plt.figure(figsize=(8, 6))
    sns.barplot(
        y="rental_count",
        x="hour",
        hue="hour",
        data=byhour_df,
        palette=colors_list,
        legend=False
    )
    plt.title("Total Bicycle Rentals by Hour", loc="center", fontsize=15)
    plt.ylabel("Total Rentals", fontsize=12)
    plt.xlabel("Hour of the Day", fontsize=12)
    plt.tick_params(axis='x', labelsize=12)
    plt.tight_layout()
    st.pyplot(plt.gcf())


hours_df['dteday'] = pd.to_datetime(hours_df['dteday'])

filtered_hours_df = hours_df[
    (hours_df['dteday'] >= selected_dates[0]) &
    (hours_df['dteday'] <= selected_dates[1]) &
    (hours_df['hr'] >= selected_hour[0]) &
    (hours_df['hr'] <= selected_hour[1])
]

col1, col2 = st.columns(2)

monthly_sum_by_year = filtered_hours_df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()

with col1:
    plt.figure(figsize=(6, 4))
    sns.lineplot(
        x="mnth",
        y="cnt",
        hue="yr",
        data=monthly_sum_by_year,
        marker="o",
        palette="Set1"
    )
    
    plt.title("Total Bicycle Rentals by Month (2011 vs 2012)", loc="center", fontsize=15)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Total Rentals", fontsize=12)
    plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.legend(title="Year", loc="upper left")
    plt.tight_layout()

    st.pyplot(plt.gcf())

hourly_sum_by_year = filtered_hours_df.groupby(['yr', 'hr'])['cnt'].sum().reset_index()

with col2:
    plt.figure(figsize=(6, 4))
    sns.lineplot(
        x="hr",
        y="cnt",
        hue="yr",
        data=hourly_sum_by_year,
        marker="o",
        palette="Set1"
    )
    
    plt.title("Total Bicycle Rentals by Hour (2011 vs 2012)", loc="center", fontsize=15)
    plt.xlabel("Hour of the Day", fontsize=12)
    plt.ylabel("Total Rentals", fontsize=12)
    plt.xticks(ticks=range(0, 24))
    plt.legend(title="Year", loc="upper left")
    plt.tight_layout()

    st.pyplot(plt.gcf())


heatmap_data = (
    filtered_hours_df.groupby([filtered_hours_df['weekday'].map(day_mapping), 'hr'])
    .agg({'cnt': 'sum'})
    .reset_index()
    .pivot_table(index='weekday', columns='hr', values='cnt', aggfunc='sum')
)

heatmap_data = heatmap_data.reindex(weekday_order)

plt.figure(figsize=(14, 6))
sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=".0f", annot_kws={"size": 8}, linewidths=0.5)

plt.title("Heatmap Bicycle Rentals by Day and Hour", loc="center", fontsize=15)
plt.xlabel("Hour of The Day", fontsize=12)
plt.ylabel("Day", fontsize=12)

plt.tight_layout()

st.pyplot(plt.gcf())

day_type_hours_df['dteday'] = pd.to_datetime(day_type_hours_df['dteday'])

filtered_day_type_hours_df = day_type_hours_df[
    (day_type_hours_df['dteday'] >= pd.to_datetime(selected_dates[0])) &
    (day_type_hours_df['dteday'] <= pd.to_datetime(selected_dates[1])) &
    (day_type_hours_df['hour'] >= selected_hour[0]) &
    (day_type_hours_df['hour'] <= selected_hour[1])
]

hourly_day_type_sum = filtered_day_type_hours_df.groupby(['hour', 'day_type'], observed=False)['sum_cnt'].sum().reset_index()

by_hour_day_type_df = pd.DataFrame({
    "hour": hourly_day_type_sum['hour'],
    "day_type": hourly_day_type_sum['day_type'],
    "rental_count": hourly_day_type_sum['sum_cnt']
})

by_hour_day_type_df = by_hour_day_type_df.sort_values(by="hour", ascending=True)

palette = {
    "Weekday": "darkblue",
    "Weekend": "lightblue"
}

plt.figure(figsize=(12, 6))

sns.barplot(
    x="hour", 
    y="rental_count", 
    hue="day_type", 
    data=by_hour_day_type_df,
    palette=palette,
    errorbar=None
)

plt.title("Total Bicycle Rentals by Hour and Day Type", loc="center", fontsize=15)
plt.xlabel("Hour of the Day", fontsize=12)
plt.ylabel("Total Rentals", fontsize=12)

plt.tight_layout()

st.pyplot(plt.gcf())


cust_type_df['dteday'] = pd.to_datetime(cust_type_df['dteday'])

filtered_cust_type_df = cust_type_df[
    (cust_type_df['dteday'] >= pd.to_datetime(selected_dates[0])) &
    (cust_type_df['dteday'] <= pd.to_datetime(selected_dates[1])) &
    (cust_type_df['hour'] >= selected_hour[0]) &
    (cust_type_df['hour'] <= selected_hour[1])
]

daily_sum = filtered_cust_type_df.groupby('weekday', observed=False).agg({
    'casual_sum': 'sum',
    'registered_sum': 'sum'
}).reindex(weekday_order)

byday_df = pd.DataFrame({
    'weekday': weekday_order,
    'casual_rental': daily_sum['casual_sum'].values,
    'registered_rental': daily_sum['registered_sum'].values
})

byday_melted = byday_df.melt(id_vars='weekday',
                             value_vars=['casual_rental', 'registered_rental'],
                             var_name='user_type',
                             value_name='rental_count')

plt.figure(figsize=(10, 6))

sns.barplot(
    x='weekday',
    y='rental_count',
    hue='user_type',
    data=byday_melted,
    palette=['lightblue', 'darkblue']
)

plt.title('Casual and Registered Rental Counts by Day', fontsize=15)
plt.xlabel('Day', fontsize=12)
plt.ylabel('Total Rentals', fontsize=12)
plt.xticks(rotation=45, ha="right")

plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title='User Type')

plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

plt.tight_layout()

st.pyplot(plt.gcf())

recency_df = filtered_hours_df.groupby(['weekday', 'hr'], as_index=False).agg({
    'dteday': 'max',
    'cnt': 'sum',
    'casual': 'sum',
    'registered': 'sum'
})

recency_df['recency'] = recency_df['dteday'].apply(lambda x: (filtered_hours_df['dteday'].max() - x).days)

recency_df['monetary'] = recency_df['cnt']

recency_df['frequency'] = recency_df['cnt'] / len(filtered_hours_df['dteday'].unique())

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4"] * 7

sns.barplot(y="recency", x="weekday", data=recency_df, palette=colors, ax=ax[0], errorbar=None)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Recency by Weekday", loc="center", fontsize=18)
ax[0].set_xticklabels(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], rotation=45)

sns.barplot(y="frequency", x="weekday", data=recency_df, palette=colors, ax=ax[1], errorbar=None)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Frequency by Weekday", loc="center", fontsize=18)
ax[1].set_xticklabels(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], rotation=45)

sns.barplot(y="monetary", x="weekday", data=recency_df, palette=colors, ax=ax[2], errorbar=None)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("Monetary by Weekday", loc="center", fontsize=18)
ax[2].set_xticklabels(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], rotation=45)

plt.suptitle("RFM Analysis by Weekday (Recency, Frequency, Monetary)", fontsize=20)

st.pyplot(fig)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
import streamlit as st
from streamlit_extras.colored_header import colored_header
sns.set(font_scale=0.8)

df = pd.read_csv("data.csv")

###Cleaning and preparing the data###
df = df.drop_duplicates() #Duplicates
df['published_time'] = pd.to_datetime(df['published_time']) #Duplicates
df['published_year'] = df['published_time'].apply(lambda x: x.year)

colors = ListedColormap(
    sns.color_palette(
        list(reversed(['#8f38eb','#4338b6','#5c9ea0','#98d8ba','#e8e643','#e09b28','#d55332']))
        ).as_hex()
    )

#Body
st.title('Udemy Analysis')
st.caption('Dataset extracted from https://www.kaggle.com/datasets/hossaingh/udemy-courses')

colors

#Preparing the palette
a= (
    df[['category','id']]
    .groupby('category',as_index=False)['id']
    .agg({'id':lambda x: x.count()/df['id'].count()})
    .set_index('category')
)

colors = list(reversed(['#8f38eb','#4338b6','#5c9ea0','#98d8ba','#e8e643','#e09b28','#d55332']))

colors = pd.qcut(a['id'],7, labels=colors)

my_cmap = ListedColormap(sns.color_palette(colors).as_hex())


colored_header(
    label="Udemy Number of Courses and Trends Analysis",
    description="",
    color_name="violet-70",
)

st.subheader('Number of Courses Created Through the Years')

fig, ax = plt.subplots()
(
    df.groupby('published_year',as_index=False)['id']
    .count()
    .plot.line(x='published_year',color='#8f38eb',figsize=(15,3),ax=ax)
)

st.pyplot(fig)

col1, col2 = st.columns([1,1])
with col1:
    st.subheader('Number of Courses Created Through the Years Divided By Category')
    
    fig, ax = plt.subplots()
    (
        df[['published_year','category','id']]
        .pivot_table(index='published_year',columns='category',values='id',aggfunc='count')
        .reset_index()
        .plot.bar(
            x='published_year',
            subplots=True,
            figsize=(20,10),
            sharex=True,
            layout=(5, 3),
            sharey=True,
            cmap=my_cmap,
            legend=False,
            ax=ax,
            #fontsize=6,
        )
    ) 
   # plt.tight_layout() 
    plt.subplots_adjust(
        left=0.1,
        bottom=0.1,
        right=0.9,
        top=0.9,
        wspace=0.05,
        hspace=0.4
    )
    st.pyplot(fig)

with col2:
    st.subheader('Total Courses Created by Category')

    fig, ax = plt.subplots()
    (
        df[['category','id']]
        .groupby('category',as_index=False)['id']
        .agg({'id':lambda x: x.count()/df['id'].count()})
        .set_index('category')
        .plot.pie(
            y='id',
            autopct='%1.0f%%', 
            figsize=(9,9),
            legend=False,
            pctdistance=0.8,
            labeldistance=1.03,
            ylabel='',
            rotatelabels =True,
            counterclock=False,
            startangle=-246,
            colors = colors,
            ax=ax
        )
    )
    plt.tight_layout()
    st.pyplot(fig)

colored_header(
    label="Udemy Monetary Analysis",
    description="",
    color_name="violet-70",
)


st.subheader('Estimate income with "Original Prices"')
df['published_month'] = df['published_time'].apply(lambda x: x.to_period('M'))
df['income'] = df['price'] * df['num_subscribers']
fig, ax = plt.subplots()
ax= (
    df
    .groupby('published_month',as_index=False)['income']
    .sum()
    .plot(
        x='published_month',
        y='income',
        figsize=(15,3),
        ax=ax,
        color='#8f38eb'
    )
)
st.pyplot(fig)

st.header('Distribution of Pricess Across the Categories')
fig, ax = plt.subplots(figsize=(15,3))
sns.set_palette(sns.color_palette(colors))
sns.boxplot(data=df,x='category',y='price',showfliers=False,ax=ax)
plt.xticks(rotation=90)
st.pyplot(fig)

col1, col2 = st.columns([3,2])
with col1:
    st.header('Historical % of Free Courses vs Paid Courses')
    a = df.groupby(
        ['published_year','is_paid'],as_index=False
    )['id'].count().sort_values(['is_paid','published_year'])
    a = a.pivot_table(index='published_year',columns='is_paid',aggfunc='sum',values='id').reset_index()
    a['total'] = a[False] + a[True]
    b = pd.DataFrame()
    b[False] = a.apply(lambda x: (x[False] / x['total']*100),axis=1)
    b[True] = a.apply(lambda x: (x[True] / x['total']*100),axis=1)
    b['published_year'] = a['published_year']
    fig, ax = plt.subplots(figsize=(15,5))
    b[['published_year',True,False]].plot.bar(x='published_year',stacked=True,color=['#8f38eb','#d55332'],ax=ax)
    plt.tight_layout()
    st.pyplot(fig,figsize=(15 ,5))

with col2:
    st.header('Cumulative Stimate Income')
    a = df.sort_values('published_month')
    a['total'] = a['income'].cumsum()
    x = a['published_month']
    y = a['total']
    fig, ax = plt.subplots(figsize=(15,6.4))
    a.plot(x= 'published_month',y='total',ax=ax)
    plt.fill_between(x, 0, y)
    st.pyplot(fig,figsize=(15,6.4))

colored_header(
    label="Udemy Quality Analysis",
    description="",
    color_name="violet-70",
)

fig, ax = plt.subplots(1,2,figsize=(12,7))

quality = df[['price','category','published_year','avg_rating']]
my_cmap2 = ListedColormap(sns.color_palette(list(reversed(['#8f38eb','#4338b6','#5c9ea0','#98d8ba','#e8e643','#e09b28','#d55332']))).as_hex())
sns.heatmap(quality.corr(),ax=ax[0],cmap=my_cmap2,annot=True)

df.groupby('category')['avg_rating'].mean().plot.bar(color='#98d8ba',ax=ax[1])
ax[0].set_title('Correlaction between variables')
ax[1].set_title('Average Rating by Category')
plt.tight_layout()
st.pyplot(fig)

st.header('Average Rating Trough the Years')
fig, ax = plt.subplots(figsize=(10,2))
df.groupby('published_year')['avg_rating'].mean().plot(color='#8f38eb')
st.pyplot(fig)

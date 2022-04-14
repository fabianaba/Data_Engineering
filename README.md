# Data_Engineering: H&M store webscrapping
[Data Engineering project using Python Beautiful Soup library, Regex, and SQL]

The Data Engineer's work can be summarized in 2 major areas: Data Architecture and Data Modeling.

In Data Architecture, the Data Engineer is responsible for creating data pipelines bringing the data from the source to the final user. Data sources can be numerous: databases, APIs, websites, etc. By users we can say data analysts, data scientists, business analysts, managers, finance departments, consumer service support, visualization tools, websites, mobile devices - in short: anyone, tool or system!

![Jeans](https://github.com/fabianaba/Data_Engineering/blob/main/images/jeans.png)

## 1. Business problem

The Star Jeans company is owned by two Brazilians friends and business partners. After several successful business, they are planning to start an E-commerce business model at the USA with  just one product and for a specific audience: jeans pants for male. The objective is to keep the cost of operation down and scale as they start growing their marketshare.
However, even with the entry product and audience defined, the two partners lack experience in this fashion market and therefore don't know how to define basic things like price, types/models of pants, and the necessary material for the manufacture.
Thus, the two partners hired a Data Science consultancy to answer the following questions:
* 1. What is the best selling price for the pants? 
* 2. How many types of pants and their colors for the initial product? 3. What raw materials are needed to make the pants?
The main competitors of the Start Jeans company are the American companies H&M and Macys.

On this first cycle of the data solution approach, the Data Engineer's objective is to collect data from the H&M website and save a dataset with all information.

## 2. Solution Strategy

The strategy adopted was the following:

<b> Step 01 - Data Collection:</b> I used webscraping techniques to collect the data and Regular Expression (Regex) to clean the data.

<b> Step 02 - Data Base creation:</b> I created a database with a table to congregate all collect data and consult them via SQL.

<b> Step 03 - ETL planning:</b> Entries containing no information or containing information which does not match the scope of the project were filtered out.

<b> Step 04 - Exploratory Data Analysis:</b> I performed univariate, bivariate and multivariate data analysis, obtaining statistical properties of each of them, correlations and testing hypothesis (the most important of them are detailed in the following section).

<b> Step 05 - Data Preparation:</b> In this step I planned the ETL (extration, transformation, and load), designed a script to automatically run the collection, and set up a log file to keep track of the tasks and possible errors.

## 3. Conclusions

The final dataset provides the enterpreneurs with valuable data about the competitor H&M that can now be used for the Data Scientist to analyze and answer the business questions above.

## 4. Next steps and improvements

The same techniques can be applied to other competitors so the dataset would bring complete information to be analyzed.

The Data Scientist would make an Exploratory Data Analysis (EDA) to uncover business insights and also apply machine learning models to forecast desirable outputs.

The model will be deployed to production in an App at Heroku so the business owners could consult the results from any device connected to the internet.

***
### References
* Blog [Seja um Data Scientist](https://sejaumdatascientist.com/)
* H&M website [H&M](https://www2.hm.com/en_us/men/products/jeans.html) 
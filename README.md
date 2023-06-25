# STEAM GAME RECOMMENDATION

![Steam Game](https://user-images.githubusercontent.com/35566310/236703142-5ab6d9e0-6ca8-419e-b712-a4625edf372a.jpg)

                                                                                      1. Nipun Hedaoo             - 40165942          
                                                                                      2. Riddhi Shah              - 40197190
                                                                                      3. Varshini Vankayalapati   - 40196495
                                                                                      4. Vishanth Surresh         - 40181942

### PROJECT SUMMARY
<p align="justify"> 
Gaming Industry is one of the fastest-growing industries in the world, with millions of gamers around the world spending countless hours playing their favorite games. With such a vast collection of games available, it can be challenging for gamers to find new games that align with their preferences. The Goal of this project is to develop a Game Recommendation System that provides personalized recommendations to video gamers to purchase a new game on Steam Website. 
</p>

<p align="justify"> 
Steam is the world's most popular PC Gaming hub, with over 6,000 games and a community of millions of gamers. In this project we used dataset provided by Kaggle, which contains information on over 200,000 purchases on multiple video games available on Steam. This dataset contains a list of user behaviors, with attributes: User-ID, Game-title, Behavior-name, value. The behaviors included are 'purchase' and 'play'. The value indicates the degree to which the behavior was performed - in the case of 'purchase' the value is always 1, and in the case of 'play' the value represents the number of hours the user has played the game.
</p>

<p align="justify"> 
In addition, we generated few features from the existing attributes, which will be very helpful for the recommendation system, For Example: Game Ratings. In this project will be implementing the following stages, Missing Values Handling, Outliers Detection, Feature Addition, Feature Selection, Exploratory Data Analysis, Hyper Parameter Tuning, Training, Testing and Validation of Machine learning model. The technology stack and development tools that will be used in this project are Python as the language, Pyspark as the Big Data framework, Google Colab and Kaggle IDE as the development environments, Github as the integration platform, and several Python libraries such as Pyspark, Numpy, CSV, and Pandas.The algorithms we are planning to implement to develop our model are Cosine Similarity, Matrix Factorization and other algorithms in Scikit Learn. Our research mostly focus on building the recommendation system with multiple algorithms and evaluate the performance between them. 
</p>

<p align="justify"> 
Furthermore, in addition to the recommendation system, classification algorithms will also be implemented to classify user behavior. This will help in understanding the user's preferences, which can further enhance the recommendations provided by the system. In conclusion, the development of a game recommendation system is an essential project in the gaming industry. The performance of these algorithms will be evaluated to determine the best algorithm that provides the most accurate and efficient recommendations for the users.
</p>

### RESEARCH QUESTIONS ADDRESSED
1. Study and develop a game recommendation system that provides personalized recommendation to video gamers to purchase a new game.
2. Multiple recommendation model is developed using  multiple algorithms and performance comparison is done between them
    a. Matrix Vectorization - ALS
    b. Item Item Recommendation - Cosine Similarity and Pearson Coefficient
3. Calculate the effectiveness of each model using Root Mean Squared Error [RMSE] and Time Taken to train the model.

### DATASET DESCRIPTION
-----------------------------------------------------------------------------------------------
| Information                      | Details                                                  |
|----------------------------------|----------------------------------------------------------|
| Dataset Size                     | 9.0 MB                                                   |
| Total number of Attributes       | 5                                                        |
| Number of New Features Generated | 5                                                        |
| Attributes                       | UserID, Steam_Game, Behaviour Name, Hours_played         |
| Total number of Datapoints       | 200 k                                                    |
| Sparsity of Utility Matrix       | 99.69 %                                                  |
| Total number of Files            | 1                                                        |
| Type                             | Recommendation System                                    |
| Kaggle Dataset Link              | https://www.kaggle.com/datasets/tamber/steam-video-games |
-----------------------------------------------------------------------------------------------

### TECHNOLOGY STACK & DEVELOPMENT
-------------------------------------------------------------------
| Category             | Technologies/Libraries/Tools             |
|----------------------|------------------------------------------|
| Language             | Python                                   |
| Big Data Framework   | PySpark                                  |
| Development          | Google Colab, Databricks                 |
| Integration          | GitHub                                   |
| Python Libraries     | PySpark, NumPy, Pandas, CSV              |
| Algorithms           | Cosine Similarity, Matrix Factorization  |
-------------------------------------------------------------------


### MODEL DESIGN
![Table](https://user-images.githubusercontent.com/35566310/236702729-11ac586e-355f-47ba-8918-ba4f3c7dad37.png)

### MODEL PERFORMANCE 
![Performance](https://user-images.githubusercontent.com/35566310/236702816-2d178501-5b53-4de9-8140-a911eac44c3d.png)

### MODEL COMPARISON
![Comparison](https://user-images.githubusercontent.com/35566310/236702945-19d5f82e-fbc9-41aa-876c-8727302ef9d8.png)


### CONCLUSION
<p align="justify"> 
After considering multiple parameters, we found that the Pearson Coefficient model outperformed the other two models. However, the training time required for the Pearson Coefficient model was longer compared to the Cosine Similarity model and ALS. Despite this, the evaluation results showed that the Pearson Coefficient model was better. 
</p>

<p align="justify"> 
Cosine Similarity and Pearson Coefficient results are almost same, only the key difference between the two models is that the Pearson Coefficient model subtracts the mean user game ratings from the rating data before calculating the similarity score, whereas the Cosine Similarity model does not. That’s why Pearson Coefficient results are slightly better than Cosine Similarity. 
</p>




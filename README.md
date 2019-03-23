# <img src="https://cdn.glitch.com/cb093bfd-142f-45b3-bdb4-52ff49e0a1c2%2Fneighlogo.png?1553305171074" height="60"> NeighborAlert

<img src="https://cdn.glitch.com/cb093bfd-142f-45b3-bdb4-52ff49e0a1c2%2FScreen%20Shot%202019-03-22%20at%206.45.19%20PM.png?1553305555812">

- Description: Missed a fun event close to where you live? Need helping moving that couch up the stairs? Heard a car alarm go off last night? Find out about whats happening in your neighborhood! Use NeighborAlert App to keep up with most current news and events in your area!

- Goal: App that brings neighbors together, promotes sharing ideas and resources, promotes communication, posting about what is new around the neighborhood.

## Core Technical Requirements Implemented:
* **Flask:** Flask as the core framework for Python.
* **PostgreSQL:** PostgreSQL for database in development and production.
* **Data Models** Include at least two data models with associations.
* **Data Validation:** Your application should validate incoming data before entering it into the database.
* **Error Handling:** Forms in your application should also validate data, handle incorrect inputs, and provide user feedback on the client side.
* **Views:** Use **Jinja templates**.
* **Home & About Pages:** Create a landing page (homepage) that clearly explains your app's value proposition and guides the user through the "get started" funnel. Create an about page that includes photos and brief bios of your team members.
* **User Experience:** Ensure a pleasing and logical user experience. Use a framework like Bootstrap, Bulma, or Skeleton to enhance and ease your CSS styling.
* **Responsive Design:** Make sure your app looks great on a phone or tablet.
* **Heroku:** Deploy your app to Heroku. Ensure no app secrets are exposed. *Do not commit secret keys to GitHub!*

## AirDrop Farer App Hierarchy:
```
App
├──  App.js
├──  App.css
├──  Nav(folder)
    └──  Nav.js
    └──  Nav.css
├──  Main(folder)
    └──  Main.js
    └──  Main.css
          └──  CityList.js
          └──  CityList.css          
                └──  City.js
          └──  PostList.js
          └──  PostList.css 
                └──  Post.js
└──  Landing
```
## Repo of Different Versions of AirDrop Farer:
[Version1](https://github.com/heggy231/New-Fullstack-WayfarerV1)

[Version2](https://github.com/heggy231/New-FullStack-V2)

[Version3 Final](https://github.com/heggy231/airdropwayfarer)

## Challenge as a Team:
- Team (overall): 
  - Restructuring our file system: We overhauled our file system for props to flow better.
  - Task delineation due to code not being up on Github
  - Making the AirDrop Farer serve on localhost
  - Gaps in technical knowledge, discovering what we didn't know
  
## Challenge as individual:
- Darnell:
  - Understanding with how frontend connects with backend
  - Managing state and passing props down


- Heggy:
  - Routing vs passing props using state
  - Understanding database concepts
  - Running the backend and frontend together

- Ghenet:
  - Making components communicate (setting and managing state)
  - Backend

## Lessons Learned (Personal area of growth, Working with a team):
- Personal area of growth: 
  - Heggy: Express routing, React State, Local storage
  - Darnell: Creating CRUD functionalities, managing state, task management (breaking down challenges into manageable tasks)
  - Ghenet: How to utilize local storage, learn about setting and managing state, learned about task management
  
- Working with a team:
  - Heggy: Communicating with team better
  - Darnell: Giving more specific and constructive in the moment feedback
  - Ghenet: Communicating with team better, Learned that working in a team is better, Healthy team means complimenting each other's strengths.

## How to run AirDrop Farer React app:
- frontend: runs on http://localhost:3000/
```
cd /frontend
npm install
```
- backend: runs on http://localhost:3001/
```
#### backend ########################
> `npm install`  // pulling down from master install the dependencies require for the project `npm i` also same
> `npm install bcrypt --save`
> `mongod` is running in a tab of Terminal.
> 'node db/seed.js' and make sure to require our models folder at the top.
> `nodemon` // test if express is working
```

```
https://media.giphy.com/media/ZI9yBW6pTpJOE/giphy.gif
```

project3 neighbor alert
readme file


Project 3 app name: NeighborAlert
Github: https://github.com/nassBouz/Project3-NeighborAlert
Trello: https://trello.com/b/FUzGsQMl/wdi-project-3-neighboralert

Project requirement spec: https://git.generalassemb.ly/sf-wdi-51/project-03

- 2 resources for heroku deployment:
  1) Link for flask app deployment on heroku- https://git.generalassemb.ly/sf-wdi-51/flask-deployment

  2) Also, Brock found this which might help too: http://blog.sahildiwan.com/posts/flask-and-postgresql-app-deployed-on-heroku/
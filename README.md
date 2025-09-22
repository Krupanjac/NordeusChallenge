# Full-stack Challenge - Engineering Mastery
Nordeus - Job Fair 2024

[![nord1](https://i.imgur.com/ViSCCYU.png)
[![nord2](https://i.imgur.com/dWvXFEO.png)

Conquer the Challenge and become a complete developer!
## Intro
On most projects at Nordeus there are 3 developer roles working together: Backend, Client,
and QA (Quality Assurance). Imagine you are a part of a small handpicked team at, and as
the only developer in the team, you will get to tackle all parts of the project that are usually done
by these three separate roles.
## About the challenge
A small game project was designed and the team needs you to use your skills to turn that
design into reality.
## Game description
Users are shown a grid map of 30x30 cells with each cell having a height value assigned to it. A
cell can either be water💧(height = 0) or land🪨(height > 0). Connected land cells represent
an island🏝️. The goal of the game is to find which island has the greatest average height.
Users can make their guess by clicking on any island and they have 3 attempts to guess the
correct island. After 3 wrong guesses or after a successful guess the game finishes and they
can choose to restart.
It's up to you to decide the appropriate representation of the cells to make it easier/intuitive for
the user to visually distinguish different heights.
## Client
The idea is to represent the grid as a matrix of heights, each height is an integer value in the
range from 0 to 1000 (inclusive). If the height is 0 the cell should be considered water 💧,
otherwise its land 🪨. Use the appropriate algorithm to figure out what the correct island is and
judge the user on their input. The average height of an island is calculated as the sum of all
of the heights in its cells divided by the number of cells the island has.

## Implementation guidelines on the client side:
● Graphical representation of the grid map
● An algorithm for determining the island with the greatest average height
● A way to know which island the user selected as their guess (clicking on any cell of an
island selects it)
● Compare the users selected island average height against the found solution
● Terminate the game if the user ran out of guesses or has won

[![image](https://i.imgur.com/2mT3FPL.png)

## Backend
We provided you with this url: “https://jobfair.nordeus.com/jf24-fullstack-challenge/test”. You
can send a GET request to it to receive 1 out of 10 of our map inputs at random. Each map
is 30 rows of 30 integer values ranging from 0 to 1000 representing the height of each cell.
Values in one row are separated by a single white space and rows are separated by a new
line (a 30x30 version of the 5x5 example above).
There is a link in the Useful Links section that you can check out to get the idea of how to
implement this request.
## QA
Describe the following things in a txt file:
● Description of bugs that came up - how you noticed and fixed them
● Ways you would test the projects of other contestants (inputs, actions you would do etc.)
● Improvements/features you would make if you had a magic wand (able to do anything
you wish for)
● Think of how some factors could affect your solution (e.g. map size, number of lives…)
Note: You can’t go wrong here, so don’t be afraid to let your imagination run wild!

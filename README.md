# jordle
A Wordle-guessing bot.

<p align="center">
    <a href="https://www.python.org/" alt="python">
        <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" /></a>
 <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/JarettSutula/jordle?color=orange">
 
</p>  

```
    ___  ________  ________  ________  ___       _______      
   |\  \|\   __  \|\   __  \|\   ___ \|\  \     |\  ___ \     
   \ \  \ \  \|\  \ \  \|\  \ \  \_|\ \ \  \    \ \   __/|    
 __ \ \  \ \  \\\  \ \   _  _\ \  \ \\ \ \  \    \ \  \_|/__  
|\  \\_\  \ \  \\\  \ \  \\  \\ \  \_\\ \ \  \____\ \  \_|\ \ 
\ \________\ \_______\ \__\\ _\\ \_______\ \_______\ \_______\
 \|________|\|_______|\|__|\|__|\|_______|\|_______|\|_______|
 ```

A wordle-guessing bot built in Python with the end goal of running on a Raspberry Pi.
Jordle uses an OOP approach to create a well-documented, easy to run program. It also allows Jordle
to run thousands of simulations easily to find data patterns, like finding the highest performing
starting guess and all sorts of interesting data.    

### **Project Goals**
Overall project goals are not set in stone - end goal is automation.
- [X] Takes input guess and shows corresponding guesses for each turn.
- [X] Use Regex to lower answer pool after each guess.
- [X] Use information theory to select guesses based on frequency in English language.
- [X] Make or find a wordle answer API to compare to each day.
- [ ] Put on a Pi to run everyday and send results.
- [ ] Store results from daily run in a database.
- [ ] Build a website that pulls from the database to showcase Jordle daily, previous runs, streaks, and more.




# Final Notes 
I have already learned a lot from making Jordle, and am looking forward to refamiliarizing myself with front end work as well. I have lots of ideas for improving Jordle, and will continue to update it in the future!
Thanks for reading and potentially trying out my program! :D
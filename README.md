# 🚀 Bybit Master Project - Lesson 1 of 1000
## Topic: Setting Up an Automated Testing Environment under UserLAnd (Ubuntu)

Welcome to my master project! This is the very first practical lesson of my planned 1000-part series. Here, I will show you how to build a professional, Python-based automated testing environment from scratch—even entirely from a mobile device or tablet using the **UserLAnd** Ubuntu terminal.

In this lesson, we configure the system environment, install dependencies, resolve code-level bugs, and execute our automated test suite using `pytest`.

---

## 📱 Step-by-Step Guide for UserLAnd / Ubuntu Users

Execute the following commands sequentially in your UserLAnd Ubuntu terminal to set up and run the environment.

### Step 1: Update the System and Install Required Packages
First, update the package manager and install Python 3, pip, virtualenv, git, and the nano text editor:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nano -y

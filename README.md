#Budget Tracker App

##Overview
The Budget Tracker App is a web-based application designed to help you track and manage your monthly budgets and expenses. It provides users with the ability to create budgets, categorize expenses, and gain insights into their financial health.

##Features
- User Management: Register and log in securely using email and password. Use JSON Web Tokens (JWT) for session management.

- Budget Management: Create, edit, and delete budgets for various expense categories. Automate monthly budget resets.

- Expense Tracking: Manually enter and categorize expenses. Expenses update associated budgets automatically.

- Expense Analysis: Calculate savings rates and debt ratios. Compare financial data from a specific day of the previous month.

- Security and Privacy: Protect user data with password hashing and secure authentication.

- Data Persistence: Maintain user data as long as the account exists.

- Email Notifications: Receive email notifications when budget limits are exceeded.

##Getting Started
1. Prerequisites: Ensure you have Python installed.
2. Installation:
```bash
pip install -r requirements.txt
```
3. Database Setup: Configure your database connection in config.py.
4. Run the Application:

```bash
uvicorn main:app --reload
```
##Usage
1. Register an account or log in.
2. Create budgets and specify spending limits for categories.
3. Record expenses, categorize them, and track your spending.
4. Gain insights into your financial health with savings rates and debt ratios.
5. Receive email notifications when you exceed budget limits.

## API Documentation
The API endpoints and documentation are available at /docs (e.g., http://localhost:8000/docs) for detailed information on how to interact with the application programmatically.

## Contributing
Contributions are welcome! Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
If you have any questions or need further assistance, please feel free to reach out to Your Name.


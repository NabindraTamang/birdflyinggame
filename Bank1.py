from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import time
import csv
import os
from datetime import datetime

console = Console()
balance = 1000
history = []
filename = "transactions.csv"

# ================= Load previous history safely =================
if os.path.exists(filename):
    with open(filename, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row.get("amount", 0))
                balance_after = float(row.get("balance_after", 0))
                history.append({
                    "timestamp": row.get("timestamp", "N/A"),
                    "type": row.get("type", "Unknown"),
                    "amount": amount,
                    "details": row.get("details", ""),
                    "balance_after": balance_after
                })
            except ValueError:
                continue
        if history:
            balance = history[-1]["balance_after"]

# ================= Utility Functions =================
def show_progress(message="Processing...", emoji="⏳"):
    with Progress(transient=True) as progress:
        task = progress.add_task(f"[green]{emoji} {message}", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.01)

def save_transaction(transaction):
    fieldnames = ["timestamp", "type", "amount", "details", "balance_after"]
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(transaction)

def colorful_history_table():
    if not history:
        console.print("📭 No transactions yet.", style="bold yellow")
        return
    table = Table(title="Transaction History", style="bold magenta")
    table.add_column("Time", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Amount", justify="center")
    table.add_column("Details", justify="center")
    table.add_column("Balance After", justify="center")
    for t in history:
        style = "bold white"  # default style
        if t["type"] == "Deposit":
            style = "bold green"
        elif t["type"] == "Withdraw":
            style = "bold red"
        elif t["type"] == "Send":
            style = "bold blue"
        elif t["type"] == "Bill Payment":
            style = "bold cyan"
        table.add_row(
            t["timestamp"],
            t["type"],
            f"{t['amount']} 円",
            t["details"],
            f"{t['balance_after']} 円",
            style=style
        )
    console.print(table)

def print_balance():
    console.print(Panel(f"💰 [bold yellow]Current Balance: {balance} 円[/bold yellow]", style="bold blue"))

# ================= Main Program =================
console.print(Panel(Text("🏦 Welcome to NABINDRA TMG BANK 🏦", justify="center", style="bold magenta"), style="bold cyan"))

while True:
    console.print("\n[bold yellow]Choose an action:[/bold yellow]")
    console.print("1. Deposit money 💰")
    console.print("2. Withdraw money 💸")
    console.print("3. Send money 📤")
    console.print("4. Pay bill 🧾")
    console.print("5. View transaction history 📜")

    choice = console.input("Enter 1,2,3,4,5: ").strip()
    if choice not in ["1","2","3","4","5"]:
        console.print("❌ Invalid choice!", style="bold red")
        continue

    if choice == "5":
        colorful_history_table()
        continue

    # Amount input
    try:
        amount = float(console.input("Enter amount (in yen): "))
        if amount <= 0:
            console.print("❌ Amount must be greater than 0!", style="bold red")
            continue
    except ValueError:
        console.print("❌ Please enter a valid number!", style="bold red")
        continue

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Deposit
    if choice == "1":
        show_progress("Depositing money...", emoji="💰")
        balance += amount
        console.print(f"🎉 Deposited {amount} 円! 🎉", style="bold green")
        transaction = {"timestamp": timestamp, "type": "Deposit", "amount": amount, "details": "Self deposit", "balance_after": balance}

    # Withdraw
    elif choice == "2":
        if amount > balance:
            console.print(f"❌ Cannot withdraw {amount} 円. Balance: {balance} 円", style="bold red")
            continue
        show_progress("Withdrawing money...", emoji="💸")
        balance -= amount
        console.print(f"✅ Withdrew {amount} 円!", style="bold red")
        transaction = {"timestamp": timestamp, "type": "Withdraw", "amount": amount, "details": "Cash withdrawal", "balance_after": balance}

    # Send
    elif choice == "3":
        receiver = console.input("Enter receiver name: ").strip()
        if amount > balance:
            console.print(f"❌ Cannot send {amount} 円. Balance: {balance} 円", style="bold red")
            continue
        show_progress(f"Sending money to {receiver}...", emoji="📤")
        balance -= amount
        console.print(f"📤 Sent {amount} 円 to {receiver}!", style="bold blue")
        transaction = {"timestamp": timestamp, "type": "Send", "amount": amount, "details": f"Sent to {receiver}", "balance_after": balance}

    # Pay bill
    elif choice == "4":
        bill_name = console.input("Enter bill name: ").strip()
        if amount > balance:
            console.print(f"❌ Cannot pay {amount} 円. Balance: {balance} 円", style="bold red")
            continue
        show_progress(f"Paying {bill_name} bill...", emoji="🧾")
        balance -= amount
        console.print(f"🧾 Paid {amount} 円 for {bill_name}!", style="bold cyan")
        transaction = {"timestamp": timestamp, "type": "Bill Payment", "amount": amount, "details": bill_name, "balance_after": balance}

    # Save transaction
    history.append(transaction)
    save_transaction(transaction)
    print_balance()

    # Continue?
    cont = console.input("Do you want to continue? (yes/no): ").strip().lower()
    if cont not in ["yes","y"]:
        console.print("Thank you for using NABINDRA TMG BANK! 👋", style="bold magenta")
        break

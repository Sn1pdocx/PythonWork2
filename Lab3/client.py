
import requests
from getpass import getpass
from tabulate import tabulate

BASE_URL = "http://127.0.0.1:5000"

FIELDS = {
    "brand": "Brand",
    "model": "Model",
    "type": "Type",
    "strings": "Number of strings",
    "color": "Color",
    "price": "Price (UAH)",
    "stock": "Stock"
}


def api_request(session, method, endpoint, **kwargs):
    try:
        response = session.request(
            method,
            BASE_URL + endpoint,
            timeout=5,
            **kwargs
        )

        print(f"HTTP status: {response.status_code}")

        data = response.json()

        if not response.ok:
            print("Error:", data.get("error", "Request failed"))
            return None

        return data

    except requests.exceptions.RequestException:
        print("Error: Unable to connect to the server.")
        return None

    except ValueError:
        print("Error: Invalid server response.")
        return None


def show_items(items):
    if not items:
        print("No guitars found.")
        return

    rows = []

    for item in items:
        rows.append([
            item["id"],
            item["brand"],
            item["model"],
            item["type"],
            item["strings"],
            item["color"],
            item["price"],
            item["stock"]
        ])

    print(tabulate(
        rows,
        headers=[
            "ID", "Brand", "Model", "Type",
            "Strings", "Color", "Price (UAH)", "Stock"
        ],
        tablefmt="grid"
    ))

    print(f"Total guitars: {len(items)}")


def input_item(current=None):
    data = {}

    for field, label in FIELDS.items():
        if current is not None:
            value = input(f"{label} [{current[field]}]: ").strip()

            if not value:
                data[field] = current[field]
                continue
        else:
            value = input(f"{label}: ").strip()

        if field in ["strings", "price", "stock"]:
            data[field] = int(value)
        else:
            data[field] = value

    return data


def input_id():
    item_id = int(input("Enter guitar ID: "))

    if item_id <= 0:
        raise ValueError

    return item_id


def show_menu():
    print("\n========== GUITARHUB ==========")
    print("1. Show all guitars")
    print("2. Show guitar by ID")
    print("3. Add guitar")
    print("4. Update guitar")
    print("5. Delete guitar")
    print("6. Search by brand")
    print("0. Exit")
    print("===============================")


def main():
    print("========== GUITARHUB LOGIN ==========")

    username = input("Username: ")
    password = getpass("Password: ")

    with requests.Session() as session:
        session.auth = (username, password)

        result = api_request(session, "GET", "/items")

        if result is None:
            print("Login failed.")
            return

        print("Authentication successful!")

        while True:
            show_menu()
            choice = input("Select an option: ")

            try:
                if choice == "1":
                    items = api_request(session, "GET", "/items")

                    if items is not None:
                        show_items(items)

                elif choice == "2":
                    item_id = input_id()

                    item = api_request(
                        session, "GET", f"/items/{item_id}"
                    )

                    if item is not None:
                        show_items([item])

                elif choice == "3":
                    print("\n--- Add guitar ---")
                    data = input_item()

                    result = api_request(
                        session, "POST", "/items", json=data
                    )

                    if result is not None:
                        print(result["message"])
                        print("New guitar ID:", result["id"])

                elif choice == "4":
                    item_id = input_id()

                    item = api_request(
                        session, "GET", f"/items/{item_id}"
                    )

                    if item is not None:
                        print("Press Enter to keep current value.")
                        data = input_item(item)

                        result = api_request(
                            session, "PUT",
                            f"/items/{item_id}", json=data
                        )

                        if result is not None:
                            print(result["message"])

                elif choice == "5":
                    item_id = input_id()

                    confirm = input(
                        "Delete this guitar? (y/n): "
                    ).lower()

                    if confirm == "y":
                        result = api_request(
                            session, "DELETE", f"/items/{item_id}"
                        )

                        if result is not None:
                            print(result["message"])
                    else:
                        print("Deletion cancelled.")

                elif choice == "6":
                    brand = input("Enter brand: ")

                    items = api_request(
                        session, "GET", "/items",
                        params={"brand": brand}
                    )

                    if items is not None:
                        show_items(items)

                elif choice == "0":
                    print("Goodbye!")
                    break

                else:
                    print("Invalid menu option.")

            except ValueError:
                print("Error: Invalid numeric value.")

            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

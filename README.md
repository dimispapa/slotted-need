<h1 align="center">SLOTTED NEED - A Product & Orders Management Application</h1>

"Slotted Need" is a Django-based web application developed to simplify the management of products, components, and order configurations for designer products such as designer tables and lamps. This app provides an easy-to-use interface to manage the complex relationships between products, components, options, and finishes, making the entire process intuitive and efficient. The name implies that this application targets the need for a system that facilitates the various components being "slotted" seamlessly between them and interacting to provide a well structured products and orders management application.

<div style="text-align:center">
<a href="https://slotted-need-bcccd2a52a21.herokuapp.com/">ACCESS THE APPLICATION</a></div>

# App Overview

## App Purpose / User Goals
The Slotted Need app aims to streamline the management of customised products and orders by offering a comprehensive interface for tracking products, components, and associated configurations. The main goals include:

- **Efficient Product Management:** Provide tools to easily manage complex relationships among products, components, options, and finishes.

- **Streamlined Order Processing:** Simplify order creation and management for internal use.

- **Customisation and Flexibility:** Enable extensive customisation options to meet client-specific needs within the defined product structures.

- **Monitoring Dashboard:** Provide a summary view dashboard portraying key information regarding sales, payments and order fulfillment.

- **Future Features:** Add features like stock & inventory management, automated client communication, component cost monitoring, and enhanced financial/sales data dashboard.

## Key Features

- **Product-Component Relationship Management:** Effectively manage products and their components, accommodating complex product builds with different components and quantities via the app administration page. Accommodate user-driven product builds via the django app admin interface.

- **Dynamic Order Forms:** Use dynamic order forms, to accurately and consistently capture product selections along with their related design options and finishes.

- **Granular Component Tracking:** Track individual components and sub-components (ComponentPart) for each product, including quantities and input costs.

- **Integration of Options and Finishes:** Manage products with multiple options and finishes that adjust dynamically based on the selected components.

- **Order Tracking:** Track and edit order details directly from the order list page, allowing inline editing with live updates to order and payment statuses, or moving completed orders to archive.

- **Order Item Tracking:** Monitor item fulfillment by tracking the item status, priority level and setting items as completed.

- **Order Archive:** Maintain an order archive with completed orders keeping a history of orders over time.

- **Filtering and Sorting Data:** Allow the filtering and sorting of data tables in the order and item trackers to facilitate drilling down and understanding data.

# App Design & Planning

## User Stories
### Must have

| Title | User Story | Acceptance Criteria |
| ----------- | ----------- | ----------- |
Admin user can login on the cloud app to access through authentication | As a User I can login on the cloud app so that I can access the app securely from any device | <ul><li>User can register as admin via email</li><li>User can sign in and sign out</li></ul> |
Add a new component/part | As a user I can add a new component input so that I can use this to populate/assemble a product | <ul><li>Can define a component's name, description, unit cost, unit measurement</li><li>Can edit or remove an existing component</li><li>Can input supplier source details</li></ul> |
Add a new product | As a user I can add a new product so that I can populate orders | <ul><li>Can add/change/delete a new product</li><li>Can link to options for finishes/configuration from the available finish categories</li><li>Can link the product with components/parts available in the system and can define quantity of each component</li><li>Can add/edit a base price for the product</li> |
Can add a category of finishes or configuration | As a user I can add a category of finishes/configurations so that I can options for relevant products | <ul><li>Can add a named category to assign options/items to it</li><li>Can edit/delete categories</li></ul> |
Can add options/items to finishes categories | As a user I can add options/items to the finishes categories so that I can populate the order form with options/configurations for a specific product | <ul><li>Can add options to a set category</li><li>Can edit/delete options</li></ul> |
Can add a new order with one or more items | As a user I can add a new order with one or more products so that I can efficiently log new orders that belong to the same customer | <ul><li>Add a new order with one or more products in the dialog box</li><li>Can delete an item from the order or change quantity</li></ul> |
Can view the totals/subtotals and can apply discount or custom price on order items | As a user I can view and manipulate the prices of order items so that I can have flexibility when submitting an order | <ul><li>Have the price displayed on the modal for each item and subtotal</li><li>Have an order total appear</li><li>Can apply a %ge discount on an order or item or apply a custom price on an item</li><li>Can add a deposit amount pre-paid on order</li> |
Can select predefined products and associated finishes/configs on order form | As a user I can select predefined products and associated finishes/configurations so that I can easily and accurately populated order items | <ul><li>Can select a product from a list</li><li>The associated options for finished/configurations dynamically appear on the order form</li></ul> |
View the full order list and fields | As a user I can view the full orders list so that I can see track and change the order details and fields | <ul><li>Can view the orders list</li><li>Can sort the table/list based on fields</li><li>Can filter the table based on select fields</li></ul> |
Set order status | As a user I can set the order status so that I can keep track of order completion | <ul><li>I can set the order status once an order is submitted</li><li>The order status options: Not started, In progress, Made, Delivered</li></ul> |
Can submit order for managing it later | As a user I can submit an order so that I can manage its progress until its fulfillment | <ul><li>User can submit the order once the order form was filled up as required</li><li>User is notified of success or failure (with reason if failed) once order form is submitted</li><li>The order object is created in the database via the post request</li></ul> |
User is notified appropriately when errors occur with suggested action or details of error | As a user I can be notified with details of an occurring error and/or suggested action so that I can react to errors and be able to report them if possible | <ul><li>Error handling is placed around the codebase with appropriate error pages displaying</li><li>Descriptive enough without compromising security by disclosing sensitive information</li><li>Have an error reporting form that will report issues to the maintaining developer</li> |


### Should have
### Could have
### Won't have

## Wireframes
### Mobile frames
### Desktop frames

## Typography & Colours
### Fonts
### Colour palette

## Database
### Design
### Implementation

## Technologies & Tools Stack
### Progamming languages
### Frameworks
### Third-party libraries

# Functionality & Features deep-dive
## Home Dashboard

## Order Management
### Create Order form
### Order Tracker view
### Item Tracker view
### Order Archive view

## Admin Portal
### Product Build Management

## User Access Management
### Access Privileges
### Logging In/Out
### Add/Invite New User
### Edit User
### Delete User

## UX

## Future Features

## Development & Deployment
### Agile development process
### Deployment to Heroku
#### How to Deploy
#### How to Clone



# Testing & Monitoring
## Manual Testing
## Automated Testing
## Code Validation
### HTML
### CSS
### JavaScript
### Python
### Lighthouse Audit
## Error Logging
## Error Monitoring
## Fixed Bugs

# Credits

# Acknowledgements

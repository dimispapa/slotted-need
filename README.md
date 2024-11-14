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
| Title | User Story | Acceptance Criteria |
| ----------- | ----------- | ----------- |
Maintaining developer can track error logs and receive error reports from users | As a maintainer developer I can review error logs and receive error reports so that I can respond and fix errors and go through error history to understand bugs | <ul><li>When an error occurs it gets logged in an error log history along with the required details: user, time of error, details of error etc</li><li>Can view an error log archived by date and can flag error items as read</li><li>Can receive error reports in email inbox as well as reported on an authorised maintainer view</li></ul> |
Can set an order as complete+paid to move them out to archive | As a user I can set an order as complete & paid so that I can move it out of existing orders into archive | <ul><li>Can click a button next to the order to declare as complete & paid</li><li>The order gets moved out from the order view into archived orders</li><li>User can move archived orders back to existing orders in case of a mistake or changes</li></ul> |
Can add client details to an order on placement | As a user I can add client details on the order placement form so that I can associate orders with clients | <ul><li>Can select a client from the Clientele list by selecting or through dynamic type search</li><li>Can add a new client with contact details if client does not exist</li><li>Can change details of a client selected on the form before submitting the order</li></ul> |
Keep track of clientele list | As a user I can keep track of clients list with contact details so that I can reach out to them when needed or select on order forms | <ul><li>Can add a client to the clientele list including contact details</li><li>Can edit/delete client details</li></ul> |


### Could have
| Title | User Story | Acceptance Criteria |
| ----------- | ----------- | ----------- |
Open an overview with key metrics | As a user I can open a key metrics view so that I can quickly assess the current situation | <ul><li>The view should include "Accrued Revenue" or "Accrued Payments"</li><li>View order items per status: "Orders made and ready for delivery", "Orders not started", "Orders in progress"</li><li>View Payments received in Current Year and Orders Fulfilled in Current Year</li></ul> |
Admin can add other users | As an Admin I can add/revoke other users with specified access privileges so that I can receive help on certain tasks when needed | <ul><li>Admin can add another user using email details</li><li>Admin can revoke a user from access</li><li>Admin can specify section or pages that the user can access</li><li>Admin can change the sectionr or pages that the user has access to</li></ul> |

### Won't have
| Title | User Story | Acceptance Criteria |
| ----------- | ----------- | ----------- |
Can drill down in Accrued revenue to see Debtor balances | As a user I can drill down further into Accrued Revenue so that I can see this amount broken down by client | <ul><li>Can access this view either from the navbar menu or the overview page by clicking on accrued revenue</li><li>This view summarises the amounts owed (or Accrued Revenue) per client, sorted descending on total amount</li></ul> |
Can view stock gaps for order fulfillment | As a user I can see what stock gaps I have so that I can plan for further stock to fulfill orders | <ul><li>Can view the stock gaps relating to components in order to fulfill existing orders</li><li>The stock gaps should flag to the user on a message when logging in or clicking on the stock view</li></ul> |
Generate a pro-form invoice based on order details | As a user I can generate a pro-form invoice based on order details so that I can accurately and easily create invoices | <ul><li>Can edit an HTML invoice template using Rich-text editor</li><li>Can choose to generate an invoice using order details</li></ul> |
Can email a client about an order using a template | As a user I can use an email template filled with order details so that I can easily email a client regarding an order | <uL><li>Can select to email a client regarding an order using an email template</li><li>Can define an email template and placeholders for order values to fill</li><li>Can register an email provider to send the email programmatically</li></uL> |
Can see if components/products are available for a selected product on the order form | As a user I can see if required components or finished products are available when selecting products on the order form so that I am aware before submitting a form | <ul><li>When a user selects a product, the relevant components or finished products stock appears flagging if there is a gap</li><li>The user can submit an order with a stock gap, however a confirmation warning message should appear to confirm</li></ul> |
Define stages of processing required for certain components | As a user I can define the stages of processing required for certain components so that I can then use these stages to track the status on the stock view | <ul><li>Can flag a component as "Processing Required"</li><li>Can define the stages of processing required to populate these in the stock view tracker</li></ul> |
Define processing stage for WIP components that require processing | As a user I can set the processing stage of a component stock item so that I can keep track of the status of components in processing | <ul><li>User can set the status of components e.g. varnished or painted</li></ul> |
Stock numbers get updated when an order is placed | As a user I can rely on the system to update the stock numbers when an order is placed so that I can keep track of my stock needs when new orders come in | <ul><li>When an order is placed, the stock components required are move to a status of "WIP" until the order is completed</li><li>The WIP items are no longer available to fulfill another order and the stock view is updated to show that</li></ul> |
Can view the stock list | As a user I can view the stock numbers per component/product so that I can keep track of stock needs | <ul><li>Have a view of products and component numbers in a tabular format</li><li>See the last time each product/component count was updated</li><li>Can edit the number/count of a line and the last updated date field will be updated automatically</li></ul> |
Can add a stock item (component or product) | As a user I can add a stock item (component or finished product) so that I can update my stock list | <ul><li>Can add a specified number of components from the available components registered in the system</li><li>Can add a specified number of products from the available products registered in the system</li></ul> |
Can keep track of a history of prices for a product | As a user I can view a history/log of prices for a given product so that I can keep track of changes over time | <ul><li>When a new price is initially set, it gets added to the history with the date</li><li>When a prices is subsequently changed, it gets added to the history along with a date and optional comment</li></ul> |
Keep track of a unit cost history of each component | As a user I can view a log of unit cost of a component each time it is changed so that I can keep track of movement over the long term | <ul><li>When a unit cost is first applied, this is added on the history with the date added</li><li>When a unit cost is then changed, this is added on the history along with the date and an optional comment</li></ul> |
Export data from the system in XLS or PDF format | As a user I can export data from the system in an excel or PDF format so that I can fulfill other needs or uses outside the app | <ul><li>Can choose what data to export</li><li>Can choose what format to export it in, between xlsx or pdf files</li></ul> |


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

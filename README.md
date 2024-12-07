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
#### Entity Relationship Diagram (ERD)
The ERD below was generated using the [graph-models](https://django-extensions.readthedocs.io/en/latest/graph_models.html) django extension which created a .dot file (see [erd_diagram.dot](documentation/erd/erd_diagram.dot)) which was then used by the [dreampuf](https://dreampuf.github.io/GraphvizOnline/) GraphViz generator to generate this diagram.
![erd](documentation/erd/graphviz-models-erd.png)

#### Products app
This is the foundation of the project, as "slotted need" revolves around design products and its configurations that then lead to orders.
- ##### Product model
    <p>The app's main model, that contains the high-level key information concerning a product, importantly <em>name</em> and <em>base_price</em>.</p>
- ##### Option & OptionValue models
    <p>These models define the design options that pertain to a product. For example a table might have a "Table Top" option which allows for various design option values such as "Cloud", "Four" or "Pick". At the same time this table could have an option for "Leg Shape" with "Husky" or "Feeble" being the available option values. Product to Option and Option to OptionValue relationships are defined as one-to-many.</p>
- ##### Component, ProductComponent, & ComponentPart models
    <p>Represents a separately identifiable component of a product e.g. a "Husky Legs" of a table. Product is linked to Component via a many-to-many relationship through the ProductComponent intermediary model. This allows for components to potentially relate to more than one product and vice versa.</p>
    <p>The ProductComponent intermediary model also captures additional information about the relationship regarding the quantity of the components that are needed to complete the product build. Optionaly, this component can be associated with a specific option value e.g. the "Husky Leg" is linked to the "Husky" option value for "Leg Shape" option. Naturally, essential components that are part the product build irrespective of option selections, will have a null option_value in this intermediary table.</p>
    <p>A component can also be broken down into granular parts of the component, captured by the ComponentPart model. e.g. a "Husky Legs" can be broken down into "Husky Top Leg" and "Husky Bottom Leg" that together make up a complete component.</p>
- ##### Finish and FinishOption models
    <p>A finish is some kind of processing applied to the finished product, such as a colour paint or oil varnish. The finish can be applied generally at product-level or more specifically at component-level, captured by the many-to-many relationships with Product and Component.</p>
    <p>FinishOption provides the selection options for each finish category e.g. "Honest Blue" for colour paint or "Linseed Oil" for oil varnish.</p>


#### Orders app
- ##### Client model
    <p>Holds key information regarding a customer and has a one-to-many relationship with the Order model, which means a client can have multiple orders for products.</p>
- ##### Order model
    <p>Defines an order which includes <em>order_status</em>, <em>paid</em> and <em>archived</em> fields to signify the status of the order, amongst other monetary fields. An order contains one or more order items.</p>
- ##### OrderItem model
    <p>This model captures the link between orders and products, with many-to-one relationships against the Order and Product models. It also holds various status and monetary fields.</p>
- ##### ComponentFinish model
    <p>This is in place to maintain the link between a component and its associated finish option applied by the order configuration selected.</p>

### Implementation
#### Products app
The products app models were implemented in the [products/models.py](products/models.py) file as follows:
| Model Name | Description | Fields | Custom Methods |
|------------|-------------|--------|----------------|
**Finish** | Represents a type of finish that can be applied to a component or product. | `name` (CharField, max_length=50), `description` (TextField, optional) | None |
**FinishOption** | Represents detailed options available for a specific finish. | `finish` (ForeignKey to Finish), `name` (CharField, max_length=50) | None |
**ComponentPart** | Represents the most granular parts of a component, including cost and quantity. | `name` (CharField, unique), `slug` (SlugField, unique), `description` (TextField, optional), `unit_cost` (DecimalField), `component` (ForeignKey to Component), `quantity` (PositiveIntegerField, default=1) | None |
**Component** | Represents high-level components that make up a product, such as legs or tops. | `name` (CharField, unique), `slug` (SlugField, unique), `description` (TextField, optional), `unit_cost` (DecimalField), `supplier_details` (TextField, optional), `finishes` (ManyToManyField to Finish, optional) | `calculate_unit_cost()`: Calculates total unit cost based on the sum of unit costs of its parts. `save()`: Ensures unit cost is calculated and updated after saving related parts. |
**Product** | Represents the main product that can be ordered, consisting of components and finishes. | `name` (CharField, unique), `slug` (SlugField, unique), `description` (TextField, optional), `base_price` (DecimalField), `components` (ManyToManyField through ProductComponent), `finishes` (ManyToManyField to Finish, optional) | None |
**Option** | Represents additional options available for a product. | `name` (CharField), `product` (ForeignKey to Product) | None |
**OptionValue** | Represents specific values for an option. | `option` (ForeignKey to Option), `value` (CharField) | None |
**ProductComponent** | Acts as an intermediary to link products with components, tracking the quantity used. | `product` (ForeignKey to Product), `component` (ForeignKey to Component), `option_value` (ForeignKey to OptionValue, optional), `quantity` (PositiveIntegerField, default=1) | None |

#### Orders app
The orders app models were implemented in the [orders/models.py](orders/models.py) file as follows:
| Model Name | Description | Fields | Custom Methods |
|------------|-------------|--------|----------------|
**Client** | Represents a customer placing an order. | `client_name` (CharField, max_length=100), `client_phone` (CharField, max_length=20), `client_email` (EmailField), `created_on` (DateField, auto_now_add=True) | None |
**Order** | Represents a customer's order. | `client` (ForeignKey to Client, optional), `discount` (DecimalField), `deposit` (DecimalField), `order_value` (DecimalField), `order_status` (IntegerField), `paid` (IntegerField), `created_on` (DateTimeField, auto_now_add=True), `updated_on` (DateTimeField, auto_now=True), `archived` (BooleanField, default=False) | `calculate_totals()`: Calculates the total discount and order value based on order items. `update_order_status()`: Updates the order status based on the statuses of related items. `save()`: Custom save method to calculate totals and update statuses as needed. |
**OrderItem** | Represents an item in an order, including the product, options, and finishes. | `order` (ForeignKey to Order), `product` (ForeignKey to Product), `base_price` (DecimalField), `discount` (DecimalField, optional), `item_value` (DecimalField), `option_values` (ManyToManyField to OptionValue, optional), `product_finish` (ForeignKey to FinishOption, optional), `item_status` (IntegerField), `priority_level` (IntegerField), `completed` (BooleanField) | `calculate_item_value()`: Calculates the value of the order item based on base price and discount. `update_completed()`: Updates the `completed` status based on item status and order payment status. `save()`: Custom save method to ensure value calculations and completed status updates. `unique_configuration()`: Generates a unique configuration string representing the product, options, and finishes. |
**ComponentFinish** | Represents finishes associated with specific components in an order item. | `order_item` (ForeignKey to OrderItem), `component` (ForeignKey to Component), `finish_option` (ForeignKey to FinishOption) | None |



## Technologies & Tools Stack

This project utilizes a robust stack of technologies and tools to deliver a seamless experience in development and functionality. This stack ensures scalability, maintainability, and ease of development, empowering the project to meet its goals effectively. Below is a breakdown of the key components:

### Programming Languages
- **[Python](https://www.python.org/)**: The core programming language used for backend logic and full-stack application development facilitated by the python-based Django framework (see below).
- **[JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)**: For dynamic front-end functionality and interactive features.
- **[HTML5](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)**: Structuring web pages with semantic markup.
- **[CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS)**: For styling the front-end and ensuring a responsive design.

### Frameworks
- **[Django](https://www.djangoproject.com/)**: A high-level, batteries-included, Python web framework that enables rapid development and clean, pragmatic design.
- **[Django REST Framework (DRF)](https://www.django-rest-framework.org/)**: For building RESTful APIs, facilitating communication between the frontend and backend.
- **[Bootstrap](https://getbootstrap.com/)**: A front-end framework for developing responsive and mobile-first web interfaces.

### Third-party JavaScript Libraries
- **[jQuery](https://jquery.com/)**: Simplifying DOM manipulation and AJAX requests for dynamic user interactions.
- **[Chart.js](https://www.chartjs.org/)**: Generates visually appealing and customizable charts for data visualization.

### Third-party Python Libraries
- **[pytest-django](https://pytest-django.readthedocs.io/en/latest/)**: Enables concise, readable, and scalable test configurations for Django projects.
- **[Unittest.mock](https://docs.python.org/3/library/unittest.mock.html)**: Used for mocking during unit testing to isolate and test the email user-invitation process.
- **[Django Model Bakery](https://model-bakery.readthedocs.io/en/latest/)**: Python library: Simplifying the creation of test data for unit tests.
- **[django-phonenumber-field](https://github.com/stefanfoulis/django-phonenumber-field)**: Ensures proper validation and formatting of phone numbers.
- **[crispy-bootstrap5](https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html#bootstrap5)**: Simplifies form rendering with Bootstrap 5 styles.
- **[django-allauth](https://django-allauth.readthedocs.io/en/latest/)**: Provides a robust authentication system, including login, registration, and third-party OAuth integration.
- **[django-crispy-forms](https://django-crispy-forms.readthedocs.io/en/latest/)**: Enhances Django forms with DRY (Don't Repeat Yourself) principles and flexible styling.
- **[django-extensions](https://django-extensions.readthedocs.io/en/latest/)**: Adds management commands and additional utilities to ease Django development.
- **[django-filter](https://django-filter.readthedocs.io/en/stable/)**: Provides filtering capabilities for Django querysets, often used with DRF.
- **[django-nested-admin](https://github.com/theatlantic/django-nested-admin)**: Adds nested inline editing functionality in the Django admin interface.
- **[whitenoise](https://whitenoise.evans.io/)**: Simplifies serving static files in production environments.

### Error Tracking/Debugging Tools
- **[Sentry](https://sentry.io/welcome/)**: For real-time error monitoring and debugging in both Python and JavaScript.
- **[Heroku](https://devcenter.heroku.com/)**: Facilitates live deployment of the application, ensuring a scalable and accessible platform.
- **[GitHub](https://docs.github.com/)**: Provides version control, secure code storage, and collaborative tools for development.
- **[Gitpod Enterprise](https://www.gitpod.io/docs/)**: Automates workspace creation directly from the GitHub repository, streamlining development setup.
- **[VS Code Desktop](https://code.visualstudio.com/docs)**: The primary IDE for code editing, debugging, and workspace management, with extensions like Python and PEP8 linters for enhanced functionality.

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

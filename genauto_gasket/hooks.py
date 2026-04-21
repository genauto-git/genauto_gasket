app_name = "genauto_gasket"
app_title = "Genauto Gasket"
app_publisher = "Genauto Gasket Technologies LLP"
app_description = "Gasket-manufacturing extensions for Genauto Gasket Technologies LLP"
app_email = "info@genautoindia.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "genauto_gasket",
# 		"logo": "/assets/genauto_gasket/logo.png",
# 		"title": "Genauto Gasket",
# 		"route": "/genauto_gasket",
# 		"has_permission": "genauto_gasket.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/genauto_gasket/css/genauto_gasket.css"
# app_include_js = "/assets/genauto_gasket/js/genauto_gasket.js"

# include js, css files in header of web template
# web_include_css = "/assets/genauto_gasket/css/genauto_gasket.css"
# web_include_js = "/assets/genauto_gasket/js/genauto_gasket.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "genauto_gasket/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "genauto_gasket/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "genauto_gasket.utils.jinja_methods",
# 	"filters": "genauto_gasket.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "genauto_gasket.install.before_install"
# after_install = "genauto_gasket.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "genauto_gasket.uninstall.before_uninstall"
# after_uninstall = "genauto_gasket.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "genauto_gasket.utils.before_app_install"
# after_app_install = "genauto_gasket.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "genauto_gasket.utils.before_app_uninstall"
# after_app_uninstall = "genauto_gasket.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "genauto_gasket.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "genauto_gasket.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"genauto_gasket.tasks.all"
# 	],
# 	"daily": [
# 		"genauto_gasket.tasks.daily"
# 	],
# 	"hourly": [
# 		"genauto_gasket.tasks.hourly"
# 	],
# 	"weekly": [
# 		"genauto_gasket.tasks.weekly"
# 	],
# 	"monthly": [
# 		"genauto_gasket.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "genauto_gasket.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "genauto_gasket.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "genauto_gasket.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "genauto_gasket.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["genauto_gasket.utils.before_request"]
# after_request = ["genauto_gasket.utils.after_request"]

# Job Events
# ----------
# before_job = ["genauto_gasket.utils.before_job"]
# after_job = ["genauto_gasket.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"genauto_gasket.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


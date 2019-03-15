
# Rackspace AutoAI Tool Specifications

## Overriding Constraints

* Simplicity – "Keep it simple" (KISS) & *Occam's Razor* rules
* Rapid implementation – only 4 days to develop during “Hack Days”
* UI style: simple, functional, free of major demo bugs

## Major Questions

1. 
2. 

## Major Use Cases

* What are the major function points the team needs to implement to get to an MVP?
* Useful for dividing up & specifying tasks to team, tracking progress and confining scope.

**Key**
* Numbered items (nearly) correspond to window mockup names in verb-noun format.
* Out-of-scope features are in a separate section below.  
* Italicized text generally indicates a question or change in initial specification.

### 1. Display Projects
* List all recognized ML projects.
### 2. Add new project
* Validate & set project name.

### 3. Upload Data
* Local file, CSV format with header only for now.

### 4. Explore Data
* Introspect uploaded input data, determining attributes (type, missing count, unique count, mean/mode, min/max) – more automatic is better for determining target, index & weight possibilities.
* Display data as rectangular columns with respective attributes.
* Populate & pre-select checkboxes for target, index & weight on each data row by name.
* Search feature to find variables quickly.
* Guide model iteration checkboxes (leave this flexible for now).
    * Select Training Type – *are we “guiding” the tool to choose or ? Regression v. Classification, only supervised learning for now.*
    * Select Loss Function – *may be automatic, depending on model type*
    * Select Model Accuracy Metric.
    * *Select # of models to train?*
* Initiate Model Training
    * Based on selected parameters train models in parallel

### 5. Train Models 

Leaderboard concept which morphs into results.
* Determine most plausible model types to try with possible hyper-parameters.
* Generate features
    1. Label Encoding
    2. Missing values & imputation
    3. One-hot encoding
* Determine top model type candidates (*is this settable?*)
* Determine hyper-parameter training space / use Scikit-Learn.RandomizedSearchCV.
* Start each model candidate job in parallel, saving results that can be later referenced.

[May be too complex as a single window--split into 2 windows?]
 
##### While training - Update model training status / leaderboard
* List % progress, elapsed training time
* List top N models with model name & validation metrics, sorted by accuracy, training time
* *Want to be able to*
    * *Unfold before completed?*
    * *Display elapsed time per candidate?*

##### Done training
* Show selected model training *results* for selected row (unfold?)
    * Model diagram
    * Model results
    * Variable importance
    * Confusion matrix (where possible)
    * Other model-type-dependent stats
* Present Deploy & Predict buttons for next step flow.
* Assume tool remembers all model results.

### 6. Predict (using selected model)
* File-based
    * Upload test data (almost identical to **Upload Data** screen above).
    * Download scored test data to local file system.
        
### 7. Deploy (using selected model)
* File-based
    * Download REST API configuration parameters

## Out-of-Scope Features

1. Login by user name
    * Simple auth, associate work with user [name, password & organization, etc.].
    * Could have various permission levels (admin, user).
2. Upload Other Data
    * xlsx, xml, gzip, json…
    * ODBC
    * HDFS
    * Other
3. Tool tips on ambiguous/busy screens to help with explanations & workflow.
4. Explainability - top features, surrogate model.

## Implementation

### Language
* Python 3.6
### User Interface
* Web-based tool – use Flask, Bootstrap, 
* Annotate each screen with common meta-data: user, model name, time/date, etc. [template this]
* Keep screen titles brief 
* Architectural pattern: Model-View-Controller (MVC)
    * Model: holds all data associated with user session
    * View: current view(s) of model for user
    * Controller: handles screen navigation by button actions

#### Reusable elements

1. Meta-data template
    * Window title (unique for multiple reasons)
    * Project name
    * Date, time

2. Upload data (for Training & Test data window)
    * Local file selector
    * Upload progress indicator

3. Single row/record of model input/output data
    * Input via window/HTML fields.
    * Output model result(s) in organized format.

4. Tabular (include sorting)
    * Data Variable Exploration
        * Name, Type, Missing, Unique, Mean/Mode, Min/Max
    * Model Training Status
        * Model type, parameters, selected accuracy, training time 
    * Confusion Matrix
        * From model training results
5. Strip graph
    * Model Training Results
    * Accuracy variations
    * Variable importance
 
#### Operational features
    
1. Logging 
* Record at key method entry/exit points using API.
* Record by user, time-date, screen name, name-value pairs at each action
* Useful for debugging and operational tracing, implement as single class.
    
#### Major Subsystems

1. Navigation/UI: event-based 
2. Data Layer
    * Abstract as Data Access Layer (DAL) with methods:
        * Load CSV file
        * Save CSV file
        * Save/load model candidate run
    * Initial implementation: persist (key:value pairs or nested dict) to file system via JSON format
    * One JSON object for training/test data, training request/result (Python dict?)
3. Task Runner (for training, we need parallelism)
    * Paradigm: producer-consumer, which decouples to async model, training threads from requests and displaying results
        * May want notification/event upon completion.
    * Make message-based? No, keep simple for now with simple API
    * API: start(), kill(), status()
    * State: start/stop times, training meta-data, etc.
4. Logging
    * Just a simple class that emits to stdout or a file (useful for debugging).
    * Record class "location", timestamp, message, key:value pairs.
    * Emit to stdout or file.

#### Diagramming
* Use https://www.draw.io/ to create diagrams

## Actors

Who interacts with the system?

* Model Developer
* API consumer
* System Admin


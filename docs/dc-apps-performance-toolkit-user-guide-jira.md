---
title: "Data Center App Performance Toolkit User Guide For Jira"
platform: platform
product: marketplace
category: devguide
subcategory: build
date: "2019-09-12"
---
# Data Center App Performance Toolkit User Guide For Jira

This document walks you through the process of testing your app on Jira using the Data Center App Performance Toolkit. These instructions focus on producing the required [performance and scale benchmarks for your Data Center app](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/).

To use the Data Center App Performance Toolkit, you'll need to:

1. [Set up Jira Data Center on AWS](#instancesetup).
1. [Load an enterprise-scale dataset on your Jira Data Center deployment](#preloading).
1. [Set up an execution environment for the toolkit](#executionhost).
1. [Run all the testing scenarios in the toolkit](#testscenario).

{{% note %}}
For simple spikes or tests, you can skip steps 1-2 and target any Jira test instance. When you [set up your execution environment](#executionhost), you may need to edit the scripts according to your test instance's data set.
{{% /note %}}

## <a id="instancesetup"></a> Setting up Jira Data Center

We recommend that you use the [AWS Quick Start for Jira Data Center](https://aws.amazon.com/quickstart/architecture/jira/) to deploy a Jira Data Center testing environment. This Quick Start will allow you to deploy Jira Data Center with a new [Atlassian Standard Infrastructure](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/) (ASI) or into an existing one.

The ASI is a Virtual Private Cloud (VPC) consisting of subnets, NAT gateways, security groups, bastion hosts, and other infrastructure components required by all Atlassian applications, and then deploys Jira into this new VPC. Deploying Jira with a new ASI takes around 50 minutes. With an existing one, it'll take around 30 minutes.

### Using the AWS Quick Start for Jira

If you are a new user, perform an end-to-end deployment. This involves deploying Jira into a _new_ ASI.

If you have already deployed the ASI separately by using the [ASI Quick Start](https://aws.amazon.com/quickstart/architecture/atlassian-standard-infrastructure/)ASI Quick Start or by deploying another Atlassian product (Jira, Bitbucket, or Confluence Data Center), deploy Jira into your existing ASI.

{{% note %}}
You are responsible for the cost of the AWS services used while running this Quick Start reference deployment. There is no additional price for using this Quick Start. For more information, go to [aws.amazon.com/pricing](https://aws.amazon.com/ec2/pricing/).
{{% /note %}}

To reduce costs, we recommend you to keep your deployment up and running only during the performance runs.

### AWS cost estimation ###
[AWS Pricing Calculator](https://calculator.aws/) provides an estimate of usage charges for AWS services based on certain information you provide.
Monthly charges will be based on your actual usage of AWS services, and may vary from the estimates the Calculator has provided.

*The prices below are approximate and may vary depending on factors such as (region, instance type, deployment type of DB, etc.)

| Stack | Estimated hourly cost ($) |
| ----- | ------------------------- |
| One Node Jira DC | 0.8 - 1.1 |
| Two Nodes Jira DC | 1.2 - 1.7 |
| Four Nodes Jira DC | 2.0 - 3.0 |

#### Stop Jira cluster nodes
To reduce AWS infrastructure costs you could stop Jira nodes when the cluster is standing idle.  
Jira node might be stopped by using [Suspending and Resuming Scaling Processes](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html).

To stop one node within the Jira cluster follow the instructions:
1. Go to EC2 `Auto Scaling Groups` and open the necessary group to which belongs the node you want to stop.
1. Press `Edit` (in case you have New EC2 experience UI mode enabled, press `Edit` on `Advanced configuration`) and add `HealthCheck` to the `Suspended Processes`. Amazon EC2 Auto Scaling stops marking instances unhealthy as a result of EC2 and Elastic Load Balancing health checks.
1. Go to `Instances` and stop Jira node.

To return Jira node into a working state follow the instructions:  
1. Go to `Instances` and start Jira node, wait a few minutes for Jira node to become responsible.
1. Go to EC2 `Auto Scaling Groups` and open the necessary group to which belongs the node you want to start.
1. Press `Edit` (in case you have New EC2 experience UI mode enabled, press `Edit` on `Advanced configuration`) and remove `HealthCheck` from `Suspended Processes` of Auto Scaling Group.


#### <a id="quick-start-parameters"></a> Quick Start parameters

All important parameters are listed and described in this section. For all other remaining parameters, we recommend using the Quick Start defaults.

**Jira setup**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Jira Product | Software |
| Jira Version | 8.0.3 or 7.13.15 or 8.5.6 |

The Data Center App Performance Toolkit officially supports:

- Jira Platform release version: 8.0.3
- Jira [Long Term Support release](https://confluence.atlassian.com/enterprise/atlassian-enterprise-releases-948227420.html): 7.13.15 and 8.5.6

**Cluster nodes**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Cluster node instance type | [m5.2xlarge](https://aws.amazon.com/ec2/instance-types/m5/) |
| Maximum number of cluster nodes | 1 |
| Minimum number of cluster nodes | 1 |
| Cluster node instance volume size | 100 |

We recommend [m5.2xlarge](https://aws.amazon.com/ec2/instance-types/m5/) to strike the balance between cost and hardware we see in the field for our enterprise customers. This differs from our [public recommendation on c4.8xlarge](https://confluence.atlassian.com/enterprise/infrastructure-recommendations-for-enterprise-jira-instances-on-aws-969532459.html) for production instances but is representative for a lot of our Jira Data Center customers.

The Data Center App Performance Toolkit framework is also set up for concurrency we expect on this instance size. As such, underprovisioning will likely show a larger performance impact than expected.

**Database**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Database instance class | [db.m5.xlarge](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#Concepts.DBInstanceClass.Summary) |
| RDS Provisioned IOPS | 1000 |
| Master (admin) password | Password1! |
| Enable RDS Multi-AZ deployment | false |
| Application user database password | Password1! |
| Database storage | 200 |

{{% note %}}
The **Master (admin) password** will be used later when restoring the SQL database dataset. If password value is not set to default, you'll need to change `DB_PASS` value manually in the restore database dump script (later in [Preloading your Jira deployment with an enterprise-scale dataset](#preloading)).
{{% /note %}}

**Networking (for new ASI)**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Trusted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Availability Zones | _Select two availability zones in your region_ |
| Permitted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Make instance internet facing | true |
| Key Name | _The EC2 Key Pair to allow SSH access. See [Amazon EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for more info._ |

**Networking (for existing ASI)**

| Parameter | Recommended Value |
| --------- | ----------------- |
| Make instance internet facing | true |
| Permitted IP range | 0.0.0.0/0 _(for public access) or your own trusted IP range_ |
| Key Name | _The EC2 Key Pair to allow SSH access. See [Amazon EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for more info._ |

### Running the setup wizard

After successfully deploying Jira Data Center in AWS, you'll need to configure it:

1. In the AWS console, go to **Services > CloudFormation > Stack > Stack details > Select your stack**.
1. On the **Outputs** tab, copy the value of the **LoadBalancerURL** key.
1. Open **LoadBalancerURL** in your browser. This will take you to the Jira setup wizard.
1. On the **Set up application properties** page, populate the following fields:
    - **Application Title**: any name for your Jira Data Center deployment
    - **Mode**: Private
    - **Base URL**: your stack's Elastic LoadBalancer URL
    Click **Next**.
1. On the next page, populate the **Your License Key** field by either:
    - Using your existing license, or
    - Generating a Jira trial license, or
    - Contacting Atlassian to be provided two time-bomb licenses for testing. Ask for it in your DCHELP ticket.
    Click **Next**.
1. On the **Set up administrator account** page, populate the following fields:
    - **Full name**: any full name of the admin user
    - **Email Address**: email address of the admin user
    - **Username**: admin _(recommended)_
    - **Password**: admin _(recommended)_
    - **Confirm Password**: admin _(recommended)_
    Click **Next**.
1. On the **Set up email notifications** page, configure your email notifications, and then click **Finish**.
1. After going through the welcome setup, click **Create new project** to create a new project.

{{% note %}}
After [Preloading your Jira deployment with an enterprise-scale dataset](#preloading), the admin user will have `admin`/`admin` credentials.
{{% /note %}}

## <a id="preloading"></a> Preloading your Jira deployment with an enterprise-scale dataset

Data dimensions and values for an enterprise-scale dataset are listed and described in the following table.

| Data dimensions | Value for an enterprise-scale dataset |
| --------------- | ------------------------------------- |
| Attachments | ~2 000 000 |
| Comments | ~6 000 000 |
| Components  | ~2 500 |
| Custom fields | ~800 |
| Groups | ~1 000 |
| Issue security levels | 10 |
| Issue types | ~300 |
| Issues | ~1 000 000 |
| Priorities | 5 |
| Projects | 500 |
| Resolutions | 34 |
| Screen schemes | ~200 |
| Screens | ~200 |
| Statuses | ~400 |
| Users | ~21 000 |
| Versions | ~20 000 |
| Workflows | 50 |

{{% note %}}
All the datasets use the standard `admin`/`admin` credentials.
{{% /note %}}

Pre-loading the dataset is a three-step process:

1. [Importing the main dataset](#importingdataset). To help you out, we provide an enterprise-scale dataset you can import either via the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script or restore from xml backup file.
1. [Restoring attachments](#copyingattachments). We also provide attachments, which you can pre-load via an [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script.
1. [Re-indexing Jira Data Center](#reindexing). For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).

The following subsections explain each step in greater detail.

### <a id="importingdataset"></a> Importing the main dataset

You can load this dataset directly into the database (via a [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script), or import it via XML.  

#### Option 1: Loading the dataset via populate_db.sh script (~1 hour)

{{% note %}}
We recommend doing this via the CLI.
{{% /note %}}

To populate the database with SQL:

1. In the AWS console, go to **Services > EC2 > Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Jira node instance.
1. Using SSH, connect to the Jira node via the Bastion instance:

    For Windows, use Putty to connect to the Jira node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/populate_db.sh && chmod +x populate_db.sh
    ```
1. Review the following `Variables section` of the script:

    ``` bash
    INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"
    DB_CONFIG="/var/atlassian/application-data/jira/dbconfig.xml"
    JIRA_CURRENT_DIR="/opt/atlassian/jira-software/current"
    CATALINA_PID_FILE="${JIRA_CURRENT_DIR}/work/catalina.pid"
    JIRA_DB_NAME="jira"
    JIRA_DB_USER="postgres"
    JIRA_DB_PASS="Password1!"
    JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
    JIRA_VERSION_FILE="/media/atl/jira/shared/jira-software.version"
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
    ```
1. Run the script:

    ``` bash
    ./populate_db.sh | tee -a populate_db.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about an hour to restore SQL database. When SQL restoring is finished, an admin user will have `admin`/`admin` credentials.

In case of a failure, check the `Variables` section and run the script one more time.
{{% /note %}}

#### Option 2: Loading the dataset through XML import (~4 hours)

We recommend that you only use this method if you are having problems with the [populate_db.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/populate_db.sh) script.

1. In the AWS console, go to **Services > EC2 > Instances**.
1. On the **Description** tab, do the following:
    - Copy the _Public IP_ of the Bastion instance.
    - Copy the _Private IP_ of the Jira node instance.
1. Using SSH, connect to the Jira node via the Bastion instance:

    For Windows, use Putty to connect to the Jira node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@${BASTION_IP}" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the xml_backup.zip file corresponding to your Jira version.

    ``` bash
    JIRA_VERSION=$(sudo su jira -c "cat /media/atl/jira/shared/jira-software.version")
    sudo su jira -c "wget https://centaurus-datasets.s3.amazonaws.com/jira/${JIRA_VERSION}/large/xml_backup.zip -O /media/atl/jira/shared/import/xml_backup.zip"
    ```
1. From a different computer, log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Restore System.** from the menu.
1. Populate the **File name** field with `xml_backup.zip`.
1. Click **Restore** and wait until the import is completed.

### <a id="copyingattachments"></a> Restoring attachments (~2 hours)

After [Importing the main dataset](#importingdataset), you'll now have to pre-load an enterprise-scale set of attachments.

1. Using SSH, connect to the Jira node via the Bastion instance:

    For Windows, use Putty to connect to the Jira node over SSH.
    For Linux or MacOS:
    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@$BASTION_IP" ec2-user@${NODE_IP}
    ```
    For more information, go to [Connecting your nodes over SSH](https://confluence.atlassian.com/adminjiraserver/administering-jira-data-center-on-aws-938846969.html#AdministeringJiraDataCenteronAWS-ConnectingtoyournodesoverSSH).
1. Download the [upload_attachments.sh](https://github.com/atlassian/dc-app-performance-toolkit/blob/master/app/util/jira/upload_attachments.sh) script and make it executable:

    ``` bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/upload_attachments.sh && chmod +x upload_attachments.sh
    ```    
1. Review the following `Variables section` of the script:

    ``` bash
    DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
    ATTACHMENTS_TAR="attachments.tar.gz"
    ATTACHMENTS_DIR="attachments"
    TMP_DIR="/tmp"
    EFS_DIR="/media/atl/jira/shared/data"
    ```
1. Run the script:

    ``` bash
    ./upload_attachments.sh | tee -a upload_attachments.log
    ```

{{% note %}}
Do not close or interrupt the session. It will take about two hours to upload attachments to Elastic File Storage (EFS).
{{% /note %}}

### <a id="reindexing"></a> Re-indexing Jira Data Center (~30 min)

For more information, go to [Re-indexing Jira](https://confluence.atlassian.com/adminjiraserver/search-indexing-938847710.html).

1. Log in as a user with the **Jira System Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver/managing-global-permissions-938847142.html).
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Full re-index** option.
1. Click **Re-Index** and wait until re-indexing is completed.
1. **Take a screenshot of the acknowledgment screen** displaying the re-index time and Lucene index timing.
1. Attach the screenshot to your DCHELP ticket.

Jira will be unavailable for some time during the re-indexing process. When finished, the **Acknowledge** button will be available on the re-indexing page.

## <a id="executionhost"></a> Setting up an execution environment

{{% note %}}
For simple spikes or tests, you can set up an execution environment on your local machine. To do this, clone the [DC App Performance Toolkit repo](https://github.com/atlassian/dc-app-performance-toolkit) and follow the instructions on the `dc-app-performance-toolkit/README.md` file. Make sure your local machine has at least a 4-core CPU and 16GB of RAM.
{{% /note %}}  

If you're using the DC App Performance Toolkit to produce the required [performance and scale benchmarks for your Data Center app](https://developer.atlassian.com/platform/marketplace/dc-apps-performance-and-scale-testing/), we recommend that you set up your execution environment on AWS:

1. [Launch AWS EC2 instance](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html). Instance type: [`c5.2xlarge`](https://aws.amazon.com/ec2/instance-types/c5/), OS: select from Quick Start `Ubuntu Server 18.04 LTS`.
1. Connect to the instance using [SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) or the [AWS Systems Manager Sessions Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).

    ```bash
    ssh -i path_to_pem_file ubuntu@INSTANCE_PUBLIC_IP
    ```

1. Install [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Setup manage Docker as a [non-root user](https://docs.docker.com/engine/install/linux-postinstall).
1. Go to GitHub and create a fork of [dc-app-performance-toolkit](https://github.com/atlassian/dc-app-performance-toolkit).
1. Clone the fork locally, then edit the `jira.yml` configuration file and other files as needed.
1. Push your changes to the forked repository.
1. Connect to the AWS EC2 instance and clone forked repository.

Once your environment is set up, you can run the DC App Performance Toolkit:

``` bash
cd dc-app-performance-toolkit
docker run --shm-size=4g  -v "$PWD:/dc-app-performance-toolkit" atlassian/dcapt jira.yml
```

You'll need to run the toolkit for each [test scenario](#testscenario) in the next section.

## <a id="testscenario"></a> Running the test scenarios on your execution environment


## Testing scenarios

Using the Data Center App Performance Toolkit for [Performance and scale testing your Data Center app](/platform/marketplace/developing-apps-for-atlassian-data-center-products/) involves two test scenarios:

- [Performance regression](#testscenario1)
- [Scalability testing](#testscenario2)

Each scenario will involve multiple test runs. The following subsections explain both in greater detail.

### <a id="testscenario1"></a> Scenario 1: Performance regression

This scenario helps to identify basic performance issues without a need to spin up a multi-node Jira DC. Make sure the app does not have any performance impact when it is not exercised.

#### <a id="regressionrun1"></a> Run 1 (~50 min)

To receive performance baseline results without an app installed:

1. On the computer where you cloned the Data Center App Performance Toolkit, navigate to `dc-app-performance-toolkit/app folder`.
1. Open the `jira.yml` file and fill in the following variables:
    - `application_hostname`: your_dc_jira_instance_hostname without protocol
    - `application_protocol`: HTTP or HTTPS
    - `application_port`: for HTTP - 80, for HTTPS - 443, or your instance-specific port. The self-signed certificate is not supported.
    - `admin_login`: admin user username
    - `admin_password`: admin user password
    - `load_executor`: executor for load tests. Valid options are [jmeter](https://jmeter.apache.org/) (default) or [locust](https://locust.io/).
    - `concurrency`: number of concurrent users for JMeter scenario - we recommend you use the defaults to generate full-scale results.
    - `test_duration`: duration of the performance run - we recommend you use the defaults to generate full-scale results.
    - `ramp-up`: amount of time it will take JMeter to add all test users to test execution - we recommend you use the defaults to generate full-scale results.
1. Run bzt.


    ``` bash
    bzt jira.yml
    ```

1. View the following main results of the run in the `dc-app-performance-toolkit/app/results/jira/YY-MM-DD-hh-mm-ss` folder:
    - `results_summary.log`: detailed run summary
    - `results.csv`: aggregated .csv file with all actions and timings
    - `bzt.log`: logs of the Taurus tool execution
    - `jmeter.*`: logs of the JMeter tool execution
    - `pytest.*`: logs of Pytest-Selenium execution

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "without app"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}

#### <a id="regressionrun2"></a> Run 2 (~50 min + Lucene Index timing test)

If you are submitting a Jira app, you are required to conduct a Lucene Index timing test. This involves conducting a foreground re-index on a single-node Data Center deployment (with your app installed) and a dataset that has 1M issues.

{{% note %}}
Jira 7 index time for 1M issues on a User Guide [recommended configuration](#quick-start-parameters) is about ~100 min, Jira 8 index time is about ~30 min.
{{% /note %}}

{{% note %}}
If your Amazon RDS DB instance class is lower than db.m5.xlarge it is required to wait ~2 hours after previous reindex finish before starting a new one.
{{% /note %}}

Benchmark your re-index time with your app installed:

1. Install the app you want to test.
1. Go to **![cog icon](/platform/marketplace/images/cog.png) &gt; System &gt; Indexing**.
1. Select the **Full re-index** option.
1. Click **Re-Index** and wait until re-indexing is completed.
1. **Take a screenshot of the acknowledgment screen** displaying the re-index time and Lucene index timing.
1. Attach the screenshot to your DCHELP ticket.

After attaching both screenshots to your DCHELP ticket, move on to performance results generation with an app installed:

    ``` bash
    bzt jira.yml
    ```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "with app"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


#### Generating a performance regression report

To generate a performance regression report:  

1. Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
1. Edit the `performance_profile.yml` file:
    - Under `runName: "without app"`, in the `fullPath` key, insert the full path to results directory of [Run 1](#regressionrun1).
    - Under `runName: "with app"`, in the `fullPath` key, insert the full path to results directory of [Run 2](#regressionrun2).
1. Run the following command:

    ``` bash
    python csv_chart_generator.py performance_profile.yml
    ```
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and summary report.

#### Analyzing report

Once completed, you will be able to review the action timings with and without your app to see its impact on the performance of the instance. If you see a significant impact (>10%) on any action timing, we recommend taking a look into the app implementation to understand the root cause of this delta.


### <a id="testscenario2"></a> Scenario 2: Scalability testing

The purpose of scalability testing is to reflect the impact on the customer experience when operating across multiple nodes. For this, you have to run scale testing on your app.

For many apps and extensions to Atlassian products, there should not be a significant performance difference between operating on a single node or across many nodes in Jira DC deployment. To demonstrate performance impacts of operating your app at scale, we recommend testing your Jira DC app in a cluster.

#### Extending the base action

Extension scripts, which extend the base JMeter (`jira.jmx`), Selenium (`jira-ui.py`) and Locust (`locustfile.py`) scripts, are located in a separate folder (`dc-app-performance-toolkit/extension/jira`). You can modify these scripts to include their app-specific actions. As there are two options for load tests executor available for selection, you can modify either Locust or JMeter scripts.

##### Modifying JMeter

JMeter is written in XML and requires JMeter GUI to view and make changes. You can launch JMeter GUI by running the `~/.bzt/jmeter-taurus/<jmeter_version>/bin/jmeter` command.

Make sure you run this command inside the `dc-app-performance-toolkit/app directory`. The main `jmeter/jira.jmx` file contains relative paths to other scripts and will throw errors if run and loaded elsewhere.

Here's a snippet of the base JMeter script (`jira.jmx`):

![Base JMeter script](/platform/marketplace/images/jmeter-base.png)

For every base action, there is an extension script executed after the base script. In most cases, you should modify only the `extension.jmx` file. For example, if there are additional REST APIs introduced as part of viewing an issue, you can include these calls in the `extension.jmx` file under the view issue transaction.

Here's a snippet of the extension JMeter script (`extension.jmx`).

![Extended JMeter script](/platform/marketplace/images/jmeter-extended.png)

This ensures that these APIs are called as part of the view issue transaction with minimal intrusion (for example, no additional logins). For a fairer comparison, you have to keep the same number of base transactions before and after the plugin is installed.

{{% note %}}
The controllers in the extension script, which are executed along with the base action, are named after the corresponding base action (for example, `extend_search_jql`, `extend_view_issue`).
{{% /note %}}

When debugging, if you want to only test transactions in the `extend_view_issue` action, you can comment out other transactions in the `jira.yml` config file and set the percentage of the base execution to 100. Alternatively, you can change percentages of others to 0.

``` yml
#      create_issue: 4
#      search_jql: 16
      view_issue: 100
#      view_project_summary: 4
#      view_dashboard: 8
```

{{% note %}}
If multiple actions are affected, add transactions to multiple extension controllers.
{{% /note %}}

##### Extending a stand-alone transaction

You can run your script independently of the base action under a specific workload if, for example, your plugin introduces a separate URL and has no correlation to the base transactions.

In such a case, you extend the `extend_standalone_extension` controller, which is also located in the `extension.jmx` file. With this option, you can define the execution percentage by the `perc_standalone_extension` parameter in the `jira.yml` config file.

The following configuration ensures that extend_standalone_extension controller is executed 10% of the total transactions.

``` yml
      standalone_extension: 10
```

##### Using JMeter variables from the base script

Use or access the following variables of the extension script from the base script. They can also be inherited.

- `${issue_key}` - issue key being viewed or modified (e.g. ABC-123)
- `${issue_id}` - issue id being viewed or modified (e.g. 693484)
- `${project_key}` - project key being viewed or modified (e.g. ABC)
- `${project_id}` - project id being viewed or modified (e.g. 3423)
- `${scrum_board_id}` - scrum board id being viewed (e.g. 328)
- `${kanban_board_id}` - kanban board id being viewed (e.g. 100)
- `${jql}` - jql query being used (e.g. text ~ "qrk*" order by key)
- `${username}` - the logged in username (e.g. admin)

{{% note %}}
If there are some additional variables from the base script required by the extension script, you can add variables to the base script using extractors. For more information, go to [Regular expression extractors](http://jmeter.apache.org/usermanual/component_reference.html#Regular_Expression_Extractor).
{{% /note %}}

##### Modifying Locust

The main Locust script for Jira is `locustio/jira/locustfile.py` which executes `HTTP` actions from `locustio/jira/http_actions.py`.
To customize Locust with app-specific actions, edit the function `app_specific_action` in the `extension/jira/extension_locust.py` script. To enable `app_specific_action`, set non-zero percentage value for `standalone_extension` in  `jira.yml` configuration file.
```yaml
    # Action percentage for Jmeter and Locust load executors
    create_issue: 4
    search_jql: 13
    view_issue: 43
    view_project_summary: 4
    view_dashboard: 12
    edit_issue: 4
    add_comment: 2
    browse_projects: 4
    view_scrum_board: 3
    view_kanban_board: 3
    view_backlog: 6
    browse_boards: 2
    standalone_extension: 0 # By default disabled
```
Locust uses actions percentage as relative [weights](https://docs.locust.io/en/stable/writing-a-locustfile.html#weight-attribute). For example, setting `standalone_extension` to `100` means that `app_specific_action` will be executed 50 times more than `browse_boards`. To run just your app-specific action, disable all other actions by setting their value to `0`.

##### Modifying Selenium

In addition to JMeter or Locust, you can extend Selenium scripts to measure end-to-end browser timings.

We use **Pytest** to drive Selenium tests. The `jira-ui.py` executor script is located in the `app/selenium_ui/` folder. This file contains all browser actions, defined by the `test_ functions`. These actions are executed one by one during the testing.

In the `jira-ui.py` script, view the following block of code:

``` python
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     app_specific_action(webdriver, datasets)
```

This is a placeholder to add an extension action. The custom action can be moved to a different line, depending on the required workflow, as long as it is between the login (`test_0_selenium_a_login`) and logout (`test_2_selenium_z_log_out`) actions.

To implement the app_specific_action function, modify the `extension_ui.py` file in the `extension/jira/` directory. The following is an example of the `app_specific_action` function, where Selenium navigates to a URL, clicks on an element, and waits until an element is visible.

To view more examples, see the `modules.py` file in the `selenium_ui/jira` directory.

#### Running tests with your modification

To ensure that the test runs without errors in parallel, run your extension scripts with the base scripts as a sanity check.

##### <a id="run3"></a> Run 3 (~50 min)
To receive scalability benchmark results for one-node Jira DC with app-specific actions, run `bzt`:

``` bash
bzt jira.yml
```

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 1"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


##### <a id="run4"></a> Run 4 (~50 min)

To receive scalability benchmark results for two-node Jira DC with app-specific actions:

1. In the AWS console, go to **CloudFormation > Stack details > Select your stack**.
1. On the **Update** tab, select **Use current template**, and then click **Next**.
1. Enter `2` in the **Maximum number of cluster nodes** and the **Minimum number of cluster nodes** fields.
1. Click **Next > Next > Update stack** and wait until stack is updated.
1. Make sure that Jira index successfully synchronized to the second node. To do that, use SSH to connect to the second node via Bastion (where `NODE_IP` is the IP of the second node):

    ```bash
    ssh-add path_to_your_private_key_pem
    export BASTION_IP=bastion_instance_public_ip
    export NODE_IP=node_private_ip
    export SSH_OPTS='-o ServerAliveInterval=60 -o ServerAliveCountMax=30'
    ssh ${SSH_OPTS} -o "proxycommand ssh -W %h:%p ${SSH_OPTS} ec2-user@$BASTION_IP" ec2-user@${NODE_IP}
    ```
1. Once you're in the second node, download the [index-sync.sh](https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/index-sync.sh) file. Then, make it executable and run it:

    ```bash
    wget https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/jira/index-sync.sh && chmod +x index-sync.sh
    ./index-sync.sh | tee -a index-sync.log
    ```
    Index synchronizing time is about 5-10 minutes. When index synchronizing is successfully completed, the following lines will be displayed in console output:
    ```bash
    IndexCopyService] Index restore started. Total 0 issues on instance before loading Snapshot file: IndexSnapshot_10203.tar.sz
    Recovering search indexes - 60% complete... Recovered added and updated issues
    Recovering search indexes - 80% complete... Cleaned removed issues
    Recovering search indexes - 100% complete... Recovered all indexes
    IndexCopyService] Index restore complete. Total N issues on instance
    ```
1. Run bzt.

    ``` bash
    bzt jira.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output. Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 2"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


##### <a id="run5"></a> Run 5 (~50 min)

To receive scalability benchmark results for four-node Jira DC with app-specific actions:

1. Scale your Jira Data Center deployment to 4 nodes the same way as in [Run 4](#run4).
1. Check Index is synchronized to new nodes the same way as in [Run 4](#run4).
1. Run bzt.

    ``` bash
    bzt jira.yml
    ```    

{{% note %}}
When the execution is successfully completed, the `INFO: Artifacts dir:` line with the full path to results directory will be displayed in console output.
Save this full path to the run results folder. Later you will have to insert it under `runName: "Node 4"` for report generation.
{{% /note %}}

{{% note %}}
Review `results_summary.log` file under artifacts dir location. Make sure that overall status is `OK` before moving to the next steps.
{{% /note %}}


#### Generating a report for scalability scenario

To generate a scalability report:

1. Navigate to the `dc-app-performance-toolkit/app/reports_generation` folder.
1. Edit the `scale_profile.yml` file:
    - For `runName: "Node 1"`, in the `fullPath` key, insert the full path to results directory of [Run 3](#run3).
    - For `runName: "Node 2"`, in the `fullPath` key, insert the full path to results directory of [Run 4](#run4).
    - For `runName: "Node 4"`, in the `fullPath` key, insert the full path to results directory of [Run 5](#run5).
1. Run the following command:

    ``` bash
    python csv_chart_generator.py scale_profile.yml
    ```
1. In the `dc-app-performance-toolkit/app/results/reports/YY-MM-DD-hh-mm-ss` folder, view the `.csv` file (with consolidated scenario results), the `.png` chart file and summary report.

#### Analyzing report

Once completed, you will be able to review action timings on Jira Data Center with different numbers of nodes. If you see a significant variation in any action timings between configurations, we recommend taking a look into the app implementation to understand the root cause of this delta.

After completing all your tests, delete your Jira Data Center stacks.

## Support
In case of technical questions, issues or problems with DC Apps Performance Toolkit, contact us for support in the [community Slack](http://bit.ly/dcapt_slack) **#data-center-app-performance-toolkit** channel.

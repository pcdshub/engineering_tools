# engineering_tools
A repository of scripts, configuration useful for the PCDS team

## Push updates
git push -u origin master


## Add Tag
git tag -a R{tag} -m '{comment}'

git push -u origin R{tag}


## Creating a new release
### Clone the source code into a new folder
git clone https://github.com/pcdshub/engineering_tools.git R{tag}
### Enter repository
cd R{Tag}
### checkout tag number
git checkout tags/R{tag}


## Updating latest
### Go to latest checkout
cd engineering_tools
### Pull latest from master branch
git pull origin master


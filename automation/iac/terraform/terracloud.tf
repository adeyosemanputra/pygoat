terraform { 
  cloud { 
    
    organization = "hari-first-project-terracloud" 

    workspaces { 
      name = "dev" 
    } 
  } 
}
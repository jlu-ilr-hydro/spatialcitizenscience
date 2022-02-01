SpatialCitizenScience
=====================

This text explains the measurement campaign. The rational and the methodology to use.
If there is a checklist to follow or a more complicated story it is a good idea 
to move it to [another page](./method)

Format
------

The page is formatted using 
[markdown](https://daringfireball.net/projects/markdown/syntax). 
Additional html tag can be used, but most tags
a stripped for security reasons. Images help to understand your content.

Structure
---------

To build your app, use the following file structure:

![directory-structure](media/directory-structure.png)

### Mandatory files and directories ###

The directory names `media` and `content` are mandatory. The `content` directory must contain the `index.md` file (you are reading it) and a `about.md` file (see [about](about)) file and .

### Optional files and directories ###

Additional files in the `content` directory eg. `xyz.md` are assessible as
`/xyz` in the browser. Subdirectories, like `method` can be browsed with
`/method`, the content of `content/method/index.md` is shown. 
The method details file `content/method/details.md` gets this URL:
`/method/details`

### Links in the navigation bar / burger menu ###

If you want to link to a page from the title menu, list it in the navigation-section of `config.yml` 

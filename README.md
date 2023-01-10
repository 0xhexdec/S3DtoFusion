# S3DtoFusion

S3DtoFusion is a Fusion360 Add-In allowing to import s3dx savefiles from Shape3d X.

## Important Note

I am aware of the fact Shape3d X offers a "3D Export" option and this Add-In might look like a way to get around the (from a hobby-shaper's perspective "massive") investment for that option to purchase. But please keep in mind: While loading the File, some slight modifications to lines and points are necessary to persuade Fusion to do what I want. Also there are some approximations done due to some fusion-internals I can not overcome and some assumptions are made how Shape3d X does, means or handles things. This Add-In is strictly made for the DIY community, who want to play around with the 3D model in Fusion360 (But please, buy at least [the standart version](https://www.shape3d.com/Products/Design.aspx) and give the devs some love) and **NOT** for professional Shapers. Also, take a look at the [known issues](#known-issues) and [file requirements](#file-requirements) to see if your board is able to be loaded properly.

## Features

Current features are:

+ Importing the modifiable 2D Bezier curves (Apex, Deck, Rail, Stringer Top/Bottom, etc)
+ Creating 3D Bezier Curves for modifiable curves (Apex, Deck, Rail, etc) - See [file requirements](#file-requirements)
+ Importing the Boxes (Finboxes, Leashplugs, etc) as 2D Sketches
+ Importing the Slices
+ Lofting the Board to a 3D Body (***experimental***)

## File Requirements

Due to the (strange) fact that Shape3d X saves all *visible* curves into the save file, but non-visable curves not (except for some special curves), it is important that you make all *modifiable* curves visible in the outline AND side views and than save the file to disc.

*Modifiable* curves are all curves you can modify within the slice view (at least Apex, Rail, Deck 1). You can make all curves visible if you like, they get imported to fusion then, but other curves than the *modifiable* ones are not necessary.

Disable all kinds of file protection!

## Known Issues

+ The Sketches are a **MESS**!
+ every form of "Non continuous" in the stringer or outline makes fusion to freak out, best to only use the **Tangent-Type: Continuous** only (that the type where both handles are fixed to each other)

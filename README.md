This was designed for IDA 6.1 QT.

While I'm aware that 6.2+ already includes a more complex version of this. This is for those people who do not
have support plans any longer and are still using IDA 6.1.

It will inject an edit line into the window allowing for filtering by regex, default is case sensitive,
just edit the source and change it or add more widgets to control it.
You may also call directly n.filter('expression', ignorecase=True)

Tested and works with Names, Functions, Strings, Imports, Exports. Pretty much any subview that uses
the same basic table view layout will work.

You can change the column to filter by changing the filterColumn kwarg on the constructor.

    There may be a way to handle this but currently I'm not aware of it.
    IDA uses its own data model/source for looking up interacting/modifying its original data
    which leads us to problems with indexing. Since we can not override functions in the original QTableView instance
    from pyside (that i know of) we can not map the index to the original source index to allow proper functionality.
    We are going to implement basic navigation functionality ourselves by remapping the doubleClicked signal. This
    will leave right click context menu operations broken but I personally never use them so this does not affect me.
    Context menus in the names/functions window will be disabled to avoid someone accidently operating on the wrong
    object and creating a mess of their IDB.
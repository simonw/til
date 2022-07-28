# Migrating a GitHub wiki from one repository to another

I figured out how to migrate a [GitHub wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis) (public or private) from one repository to another while preserving all history.

The trick is that GitHub wikis are just Git repositories. Which means you can clone them, edit them and push them.

This means you can migrate them between their parent repos like so. `myorg/old-repo` is the repo you are moving from, and `myorg/new-repo` is the destination.

    git clone https://github.com/myorg/old-repo.wiki.git
    cd old-repo.wiki
    git remote remove origin
    git remote add origin https://github.com/myorg/new-repo.wiki.git
    git push --set-upstream origin master --force

This will entirely over-write the content and history of the wiki attached to the `new-repo` repository with the content and history from the wiki in `old-repo`.

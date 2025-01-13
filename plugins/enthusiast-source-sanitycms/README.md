# Enthusiast Source Sanity CMS

This Enthusiast plugin enables the import of document data from Sanity CMS.

# Usage
Assumption: schema type looks like this:
```
export default {
    name: "blogPost",
    type: "document",
    title: "Blog Post",
    fields: [
      { name: "title", type: "string", title: "Title" },
      { name: "content", type: "array", title: "Content", of: [{ type: "block" }] },
    ],
  };
```
Fetch all blog posts using below commands:
```
from source import SanityCMSDocumentSource
s = SanityCMSDocumentSource(1, {'project_id': 'your-project-id-here', 'dataset': 'production', 'schema_type': 'blogPost', 'title_field_name': 'title', 'content_field_name': 'content'})
s.fetch()
```

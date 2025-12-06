---
description: Automate the weekly creation and publishing of a blog post for AXcent Dance Studio, including AI-generated imagery.
---

# Weekly Blog Post Automation

This workflow automates the research, writing, image generation, publishing, and notification process for the weekly blog post.

## 1. Research Phase
1.  **Search the Web**: Use `search_web` to find current trends in Bachata and Latin Dance.
    *   *Queries*: "trending bachata songs this week", "latin dance challenges [current month]", "beginner dance tips motivation", "bachata sensual news".
    *   *Goal*: Select one high-potential topic (e.g., a new song, a common beginner struggle, or a trending style).

## 2. Content Creation
1.  **Draft the Post**: Based on the research, write a 600-word blog post.
    *   *Tone*: Energetic, welcoming, knowledgeable.
    *   *Structure*:
        *   **Catchy Title** (SEO optimized).
        *   **Introduction** (Hook).
        *   **Main Body** (3-4 sections with headers).
        *   **Conclusion** (Encouraging).
        *   **Call to Action**: "Ready to move? Join us at Axcent Dance Studio this week!"
    *   *Format*: HTML (ready to be inserted into a file).


## 3. Publishing
1.  **Create New File**: Create a new HTML file for the post (e.g., `blog-posts/post-[topic-slug].html`).
    *   *Template*: Use the standard header/footer from `index.html` and the blog post layout.
    *   *Content*: Insert the drafted text.
3.  **Update Blog Listing**: Add a new entry to the top of the grid in `blog.html` linking to the new file.
    *   *Details*: Include the Title, Date/Category, Excerpt, and Link.

## 4. Notification
1.  **Notify User**: Use `notify_user` to simulate the email notification.
    *   *Subject*: "[Published] Weekly Blog Post: [Post Title]"
    *   *Body*: Link to the new post and a brief summary.
    *   *Note*: If any errors occur, provide the draft text in the notification.

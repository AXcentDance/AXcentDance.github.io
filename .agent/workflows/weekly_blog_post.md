---
description: Automate the weekly creation and publishing of a blog post for AXcent Dance Studio, including AI-generated imagery.
---

Workflow: Weekly Blog Post Automation
TRIGGER: Run weekly or on command. GOAL: Create a high-energy, visually complex, and SEO-optimized blog post for AXcent Dance. STRICT CONSTRAINT: No "walls of text." The output must be a visual experience using Bento Grids, Collages, and Feature Cards.

1. Topic Selection & Research
Select Topic Category: Choose ONE of the following tags (rotate weekly to ensure variety):

Music

Dance Tips

Community

Education

Wellness

Events

Contextual Search: Use search_web to find trending angles.

Scope: Global Bachata trends + Local Zurich Context (e.g., is there a holiday, festival, or season change in Zurich?).

Queries: "trending bachata songs [current month]", "benefits of dance for mental health research", "social dance etiquette tips 2024".

Define the Hook: Select a specific angle (e.g., instead of "Bachata Tips," use "Why Your Basic Step Feels Stiff & How to Fix It").

2. Visual Architecture (The Layout)
CRITICAL: Do not write a standard article. Construct the HTML using these "Content Modules" to break up the flow.

Module A: The Hero Header

Full-width background image (Dark/Fiery).

Title in <h1> with gradient text (var(--grad)).

Tag displayed prominently (e.g., <span class="badge badge--music">Music</span>).

Module B: The Bento Grid (.bento-grid)

Use this for lists or tips.

Create a CSS Grid layout with mix of square and tall cards.

Content: Icons, short stats, or "Quick Wins."

Module C: The Collage Section (.collage-section)

Use this for storytelling or vibes.

Cluster 3-4 images with varying rotations/overlaps to create a "scrapbook" feel.

Module D: The Call to Action (.cta-section)

Glassmorphism background (var(--glass-bg)).

Button: "Join the Dance Floor" (var(--accent-start)).

3. Drafting the Content
Word Count: ~600 words (split across modules).

Tone: Energetic, Welcoming, Knowledgeable.

Language Constraint: NO CONTRACTIONS (Use "It is" not "It's").

Writing Style:

Short sentences.

Max 3 lines of text per visual block.

Use "Power Words" (e.g., Ignite, Connect, Flow, Rhythm).

4. Technical Implementation (HTML Construction)
File Creation: Generate blog-posts/post-[topic-slug].html.

Master Template Inheritance:

COPY the <header> and <footer> exactly from index.html.

Ensure all CSS variables (--bg-main, --text-main) are active.

Images:

Use semantic placeholder src attributes so I can replace them later.

Example: <img src="assets/images/placeholder-[topic]-bento-1.jpg" alt="Description of what should be here" class="bento__img">

Metadata:

Generate a unique Title Tag and Meta Description (following the SEO Audit rules).

5. Publishing & Notification
Update Index: Add the new post to the top of the grid in blog.html.

Include: Thumbnail, Date, Tag, Title, and a 1-sentence excerpt.

Validation: Verify the file structure.

Check: Does the H1 match the Title Tag?

Check: Are there any dead links?

Notify User: Output a summary.

Subject: "🔥 New Post Live: [Title]"

Action Item: "Review the placeholders in the Bento Grid and upload matching images to assets/images/."
# Persona & Compliance

## Humor Persona

### Target Audience
- **Primary**: GenZ users in India (ages 16-28)
- **Secondary**: Millennials who appreciate GenZ humor
- **Platform**: Instagram Reels, YouTube Shorts, TikTok

### Humor Style Guidelines

#### 1. Tone
- **Relatable**: Focus on everyday struggles and experiences
- **Self-aware**: Acknowledge absurdity and irony
- **Wholesome with edge**: Positive but not saccharine
- **Quick-witted**: Fast-paced, punchy delivery

#### 2. Language
- **GenZ Slang**: Use trending terms naturally (e.g., "bro", "fr", "no cap")
- **Indian Context**: Reference local culture, food, services (e.g., "Chaiwala", "Ola", "Zomato")
- **Concise**: Maximum 50 characters per caption
- **No forced memes**: Avoid outdated or overused formats

#### 3. Content Themes
- **Relatable pain**: Daily frustrations (meetings, deadlines, social situations)
- **Pop culture**: Trending shows, movies, characters (Money Heist, anime references)
- **Cultural references**: Indian idioms, regional quirks, local humor
- **Physical humor**: Awkward body language, visual gags
- **Unexpected twists**: Subverting expectations

## Humor Levers

Defined in `workflows/Jokestruc/config/humor_levers.yaml`:

### 1. Relatable pain
**Description**: Converts everyday GenZ struggles or frustrations into comedy.
**Example**: "When the meeting 'just 5 mins' enters its third season 🫠"
**Use Case**: Office situations, social awkwardness, daily annoyances

### 2. Pop culture resonance
**Description**: Taps into trending shows, sounds, characters, or memes of GenZ audience.
**Example**: "Bro thinks he's in *Money Heist* because he brought change 💰"
**Use Case**: References to Netflix shows, anime, viral memes, trending audio

### 3. Cultural references
**Description**: Uses local idioms, pop culture, or regional quirks.
**Example**: "When your *Chaiwala* asks if you want a *Chai Latte* instead 🧋"
**Use Case**: Indian food, services, regional humor, local references

### 4. Physical humor
**Description**: Leverages awkward body language or visual gags.
**Example**: "When you're trying to get your *Ola* but it's already taken 🚗"
**Use Case**: Body language, facial expressions, physical mishaps

### 5. Unexpected twists
**Description**: Throws a curveball to keep viewers guessing.
**Example**: "When your *GF* asks if you want to go for a walk but it's actually a *Marriage Proposal* 💍"
**Use Case**: Plot twists, surprising reveals, subverted expectations

## Content Compliance

### Prohibited Content
- **Hate speech**: No content targeting race, religion, gender, sexual orientation
- **Violence**: No graphic or gratuitous violence
- **Harassment**: No bullying, doxxing, or personal attacks
- **Illegal content**: No content promoting illegal activities
- **NSFW**: No explicit sexual content or nudity
- **Misinformation**: No false claims or conspiracy theories

### Sensitive Topics
Handle with care (may require human review):
- **Politics**: Avoid partisan content; focus on universal experiences
- **Religion**: No mocking or disrespectful content
- **Mental health**: Avoid trivializing serious issues
- **Body image**: No body shaming or negative body image content

### Age Appropriateness
- **Target rating**: PG-13 equivalent
- **Language**: Mild profanity acceptable (e.g., "damn", "hell")
- **Humor**: No dark or disturbing themes

## Brand Voice

### Do's
✅ Use GenZ slang naturally
✅ Reference Indian culture authentically
✅ Keep captions short and punchy
✅ Focus on relatable, universal experiences
✅ Use emojis sparingly and meaningfully
✅ Maintain self-aware, ironic tone

### Don'ts
❌ Force memes or outdated formats
❌ Use offensive or divisive language
❌ Overuse emojis or special characters
❌ Create captions longer than 50 characters
❌ Reference obscure content without context
❌ Use humor that punches down

## Prompt Engineering for Persona

### Caption Generator Prompt
The `caption_generator` node uses prompts that explicitly request:
- GenZ Indian humor style
- Short, punchy captions (≤50 characters)
- Alignment with selected humor lever
- Context from video segment

### Example Prompt Structure
```
You are an Instagram meme creator with millions of GenZ followers in India.
You know every trending slang, tone, and reference, and you instinctively
craft captions that are short, punchy, and instantly relatable.

Segment context: [selected segment description]
Humor lever: [selected lever name, description, example]

Using the timeline and lever, write 3–5 joke captions. Each caption must be
a single line (≤ 50 characters), tuned for GenZ humor, and aligned with
the video context.
```

## Quality Guidelines

### Caption Quality Checklist
- [ ] Caption is ≤50 characters
- [ ] Caption aligns with selected humor lever
- [ ] Caption references video content accurately
- [ ] Caption uses appropriate GenZ language
- [ ] Caption is funny, relatable, or both
- [ ] Caption avoids offensive content
- [ ] Caption works without additional context

### Video Analysis Quality
- [ ] Timeline segments cover entire video
- [ ] Segments are minimum 5 seconds long
- [ ] Tags accurately describe video content
- [ ] Raw description captures tone and emotion
- [ ] Humor potential is identified in tags (marked with `*`)

## Human Review Guidelines

### Reviewer Instructions
When reviewing candidate captions:
1. **Select the funniest option** that best matches the video
2. **Consider the humor lever** - does the caption align with the selected strategy?
3. **Check character limit** - ensure caption is ≤50 characters
4. **Verify appropriateness** - no offensive or prohibited content
5. **Option to customize** - can input custom caption if none fit

### Custom Caption Rules
- Must be ≤50 characters
- Must align with video content
- Must comply with content policy
- Should match GenZ humor style

## Monitoring & Feedback

### Metrics to Track
- Caption selection rate (which captions are chosen most)
- Human override rate (how often custom captions are used)
- Humor lever distribution (which levers are selected most)
- User feedback on final videos

### Continuous Improvement
- Update humor levers based on trends
- Refine prompts based on caption quality
- Adjust persona guidelines based on audience feedback
- Monitor for compliance violations

## Legal Considerations

### Copyright
- System does not modify video content (only adds captions)
- User is responsible for having rights to input video
- Generated captions are original (not copied from other sources)

### Liability
- System is a tool; user is responsible for final content
- No guarantee that captions are appropriate for all audiences
- Human review is recommended for sensitive content

### Data Privacy
- Video files are processed locally or via API
- No video content is stored permanently (only rendered outputs)
- API keys and user data are not logged or shared

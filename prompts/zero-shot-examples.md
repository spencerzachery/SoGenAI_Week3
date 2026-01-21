# Zero-Shot Prompting Examples

Zero-shot prompting asks the model to perform a task without providing examples.

## Basic Zero-Shot

```
You are an AWS support specialist.
A customer asks: "How do I increase my EC2 instance limit?"
Provide a helpful response.
```

## Structured Zero-Shot

```
You are an AWS Enterprise Support specialist.

Task: Answer the customer's question about AWS services.
Format: Provide step-by-step instructions when applicable.
Tone: Professional but friendly.

Customer Question: How do I request a service limit increase?

Response:
```

## Zero-Shot with Constraints

```
Answer the following AWS support question.

Rules:
- Be concise (under 200 words)
- Include specific AWS console paths
- Mention relevant documentation links

Question: What should I do if my Lambda function times out?
```

## When to Use Zero-Shot

- Simple, well-defined tasks
- When the model has strong training on the topic
- Quick interactions where examples aren't needed
- General knowledge questions

Chad Walker: Hi, I'm Chad Walker. I'm an architect at Palantir. Today I have Daniel, the CTO of Gallatin. Thanks for joining me.

Daniel Buchmueller: Hey, thanks for having me.

Chad Walker: So what is Gallatin? What do you guys do?

Daniel Buchmueller: We build, I would say we rebuild, defense logistics. We're a startup. We were founded officially on the 1st of July 2024, so we're not that old yet. We're a startup, so we're quite humble. We start somewhere small. Right now we're solving tactical resupply, and we've built essentially everything on top of Palantir Foundry.

Chad Walker: That's pretty cool. So when we say tactical resupply, that means, okay, I'm out on the battlefield and I need supplies to replenish my team. What does that mean? Give a little flavor for people.

Daniel Buchmueller: Yeah. I think the best interaction is between brigade and battalion, so thousands of soldiers. They need to eat, they need to drink, they need rounds of ammunition, medical supplies, building materials, fuel, obviously. We make the process of sensing what are the supplies that they are low on. We create courses of action for, traditionally, the S4 officer, and then plan convoys and dispatch convoys to resupply.

Daniel Buchmueller: It sounds very simple. It's the most foundational set of processes that exist today. It's done very, very manually, and we started to automate a lot of these very mental processes with software.

Chad Walker: Yeah, that's pretty cool. I think about this manual process: it's phone calls, emails, spreadsheets, all these things being exchanged back and forth, and it's hard to be very prescriptive. Everything's very reactive about it, and then we're struggling to get things to the right place at the right time. It sounds like the software you're building is really to try to connect that whole process together from the front line and giving that demand signal back so we get convoys moving, getting the troops resupplied as they need it so they're not lacking anything along the way.

Daniel Buchmueller: Yeah, exactly. We all know that you don't win a war with logistics, but you certainly lose them if you don't have your act together.

Chad Walker: So how did you get started as a company with your co-founder, and then how did you really get started in the Palantir ecosystem too?

Daniel Buchmueller: We're three co-founders. Woody Glier is our co-founder and CEO. I'm Daniel Buchmueller, co-founder and CTO, and then we have Brian Ballard, who is our head of product, chief product officer.

Daniel Buchmueller: We all come from very different backgrounds. Woody most recently was at Scale, and Palantir a long time ago. Brian had his own startup that successfully exited in the augmented reality and warehouse optimization space. My past is I was at Amazon a long time ago. I co-founded Amazon Prime Air, and that was a long time ago. Since then I built engineering teams at mostly deep tech startups ranging from tele-driving, self-driving, more drone delivery, and most recently I built up the engineering team at Vast Space, so we built a commercial space station in low Earth orbit.

Daniel Buchmueller: Then Woody and I got together in spring 2024 and were introduced through 8VC, who led our seed round. This is really an important problem to solve, and it's one of these problems that is so unsexy. If you think about AI being used in intelligence and in C2 in a defense context, logistics is really left in the dust because it's always kind of a stepchild. It doesn't really see the true investments. I think Joe Lonsdale saw that potential a long time ago and was looking for the right moment and built the right team, and so that's how we started.

Chad Walker: So, okay, definitely there's the Palantir heritage amongst your founders, amongst your investors. I see in the background there, I think, a four-time winner at DevCon. You've been really building on Palantir, involved in the developer community. You're building your startup on Palantir. Why?

Daniel Buchmueller: It's interesting, right? Full disclosure: before co-founding Gallatin, I heard about Palantir. I didn't really consider it as a cloud provider. The thing is, when you deploy into mission-critical environments, such as anything in defense obviously, but other fields as well in enterprises, you really need a partner or a cloud provider where from day one you can be assured that what you're doing comes with the required safeguards.

Daniel Buchmueller: A lot of times there are requirements. If you deploy to an Army customer, there are very specific requirements. Can you be Impact Level 5, or IL5, compliant? IL6 is another, higher level. The main reason we did this, and we would do this any second again, is because it just got us to serving our customers with software much, much faster. I couldn't imagine another scenario, a faster scenario.

Daniel Buchmueller: For us, you can imagine for the startup, the zero to one is like everything is about speed. And then once you're there, meaning once you deploy to customers, how can you iterate quickly? This is not an antiquated process of burning CD-ROMs or something like that. Because you're in a protected environment, with the right access tokens you can deploy, go through all the security checks, but you can actually release on a weekly or every other week basis into Maven Smart System. That's super, super exciting for us, to be able to deliver software to our customers in hours basically, rather than days or weeks.

Chad Walker: Yeah, I love that. That's a thing I hear a lot about: software engineers are like, give me the raw tools in AWS or Azure or somewhere else. Let me go build my software and let me be a software engineer. But in Palantir, it's too abstract or this or that. But I hear you being focused on the outcomes that matter for my customer, and Palantir helps me get there faster, but I can still do the real engineering work. It's this balance that is different and I think normally kind of makes me feel uncomfortable, but embracing that focus on speed and outcome, even in these highly contested environments or in these secure environments, that's what it's about.

Daniel Buchmueller: That's exactly right. I think the other element is, Palantir is now a huge company, at least from number of employees and market capital. We're small. We're like 40, 45 people now, built that up from scratch in nine months. But we have a joint Slack channel with you all and there's like 120 people, when I last checked, in our joint Slack channel. As you know, we're just 40-plus people, and I can tell you not all employees of Gallatin are in that joint Slack channel.

Daniel Buchmueller: What I'm trying to say in a long-winded way is that the attention to feedback from Palantir is unmatched. We complain a lot. We have feature requests. We find a lot of bugs. The amazing thing is, you guys care. Palantir cares to hear feedback and implement that very quickly. Sometimes it's a P0 ticket on Palantir's side that we trigger. Being part of building this, it feels like being part of building the platform together. We're obviously a customer. I think the DevCon series has been amazing because it really brings back together all these engineers from the customer side as well as the Palantir side.

Chad Walker: Yeah, that's awesome. All right, should we take a look at some cool product and demo?

Daniel Buchmueller: Yeah, let's do it.

Chad Walker: All right, walk me through it here.

Daniel Buchmueller: Cool. This is Navigator, deployed into Maven Smart System. We're looking at a demo instance here, obviously unclassified, so notional data. Let's dive into our demo unit, which is the 3rd IBCT.

Daniel Buchmueller: What this shows you is a logistics common operating picture. It shows you at one glance how we're doing, how the units are doing. Just to give you a little bit of guidance, the color coding is absolutely standard in defense logistics. Essentially, you can see over here, these are what are called classes of supplies indicated here. Green obviously means good. Yellow, you can set the thresholds, but it's around maybe 60%. Red is below that. Black is like you're basically in trouble.

Daniel Buchmueller: What you're trying, generally speaking, to optimize for is that the unit has what's called days of supply for roughly three days. That's kind of the rhythm for how supplies are planned. You want to basically make sure that with the current supplies, they can sustain themselves for about three days. That's really what's indicated here. As a result, a lot of times you see that time horizon as well, and in this case up to 96 hours, not just 72 hours.

Daniel Buchmueller: What we can do here is dive into a specific unit. We'll pick the 3-4 CAV and go straight to the inventory. What we're seeing here is an overview of that unit's inventory on hand, what they expect to have in 24 hours, 48, and so on. What you have to understand here is these are not actual values. These are models, predictions from Navigator, and obviously can be overwritten by a human at any point in time. The human is always in control.

Daniel Buchmueller: Let's play through a scenario of our core workflow. Let's say we just heard over radio that their MREs, so that stands for meals ready-to-eat, got totally wiped out. Food is important. We save this. Essentially what we're seeing here is we're generating courses of action. This is usually done over hours by a whole team, and we already see here now course of action is updated.

Daniel Buchmueller: What that means in reality is that we obviously need to supply them. We can go to the LOGSYNC matrix. The LOGSYNC matrix is a very standard tool to understand the movements of convoys, resupply convoys. Usually you hold a LOGSYNC meeting twice a day. That's kind of the rhythm. So we can expect here the 3-4 CAV. Let me see. 3-4 CAV is down here. They need to be resupplied. Let me just make sure. Yep, that's 3-4 CAV.

Daniel Buchmueller: You can see the dates are totally off here. We have a time simulation aspect here. Our users love using this in wargaming scenarios, and so that's why you can actually simulate time. That's why it's not the real time showing here. And then, yeah, we can see the load plan. That's exactly right. It shows that we're currently at zero MREs. We're going to resupply them with 257, and then they're going to be at 257, of course.

Daniel Buchmueller: This breaks down. You can see what the convoy is made up of, and we'll see MREs showing up here. You can see utilization of the actual underlying what we call prime movers, so transporting assets essentially. That's the bread and butter. You approve a convoy, and then that gets dispatched.

Daniel Buchmueller: In the case of autonomous convoys, we can do this automatically. We've worked with Kodiak during an exercise in Hawaii at Schofield Barracks, where we demonstrated the whole resupply workflow from sensing that there's a shortfall at a downrange unit, to coming up with a course of action, to automatically dispatching one of the retrofitted Ford F-150 trucks, autonomous, fully automated end-to-end. That's the core.

Chad Walker: As long as you just play this back, I can listen to radio traffic. I can look for other signals of things, automatically understand what that means, understand the overarching orders that I have and the importance of the resupply of different components. I can then create convoys, now even dispatch autonomous convoys, to be able to actually get that resupply out to the different groups in the field, all coordinated through one piece of software as part of Maven and what Gallatin is doing.

Daniel Buchmueller: That's right. Obviously it's early days in terms of autonomous resupplies, but we very well understand that if you send out a convoy with fuel without needing a human onboard, it's much, much safer overall. If you can send out, instead of a column of convoy vehicles, more like a swarm autonomously, again, you have a much higher survivability of the actual supplies reaching the destination. I think these are critical components to building new types of defense logistics. And yes, we're supporting that with Navigator today.

Chad Walker: Yeah, that is very cool. I appreciate you taking the time to show me this. This is pretty interesting to see that, like you said, the unsexy things, but they're just so important to have all the right supplies at the right place at the right time. There's a lot of crossover between the stuff I work on in commercial and this space, but it goes back to that exact same concept of I have to have the right stuff at the right place, right time. Now you have different requirements and environments you're working in and other things. I think it's neat that you're adapting all of these things to really meet people where they are.

Daniel Buchmueller: Yeah. At Gallatin, we believe in building beautiful software that is fast, solves the problem, and is super responsive. I think everyone is used to amazing apps from Walmart, Amazon, right? They're used to getting things in the next couple of hours, or one- or two-day delivery. We just feel the warfighter deserves the same in terms of defense logistics. Again, what we just talked about is tactical resupply, but this is just the start. There's so much more that is broken that we feel we can fix and just make the life much, much easier, and more successful outcomes ultimately.

Chad Walker: Yeah. To that point, I guess maybe what are you excited about? There's so much going on in the tech world. There's all the stuff going on in defense tech. What are you excited about?

Daniel Buchmueller: Computer use agents. People generally speak about computer use agents, so the fact that it can use your computer like you are able to do, that's exciting. The asynchronous nature is what really fascinates us. I would say that's a bit further outlook. We're experimenting with that. I think what you guys introduced with long-running agents in Foundry makes a lot of sense. It's a step towards that.

Daniel Buchmueller: A lot of times we're already seeing that you have agentic workflows that do take minutes, or in the dozens of minutes already, because they're chains of agents working on a resupply solution, for example. I think the other thing that we are excited about is what we talked about earlier, of the supply signals. You want to make it as easy as possible for the warfighter not to have to enter LOGSTATs manually in a keyboard. That's definitely supported. That's the core workflow today. But obviously the best, what we say, the best LOGSTAT is no LOGSTAT, meaning it's automatically sensed.

Daniel Buchmueller: We're working on integration with, let's say, fuel level. Believe it or not, fuel is still measured with dipsticks in what's called bulk fuelers. So 2,500 gallons, someone goes with a dipstick, measures how high up the wetness is from the fuel, and then reports that. Those are simple scenarios we're working on to start to build an end-to-end feedback cycle that doesn't need human input for these basic consumption cycles.

Chad Walker: Yeah. It comes back to the OODA loop, right? Everything still seems to be focused on OODA loop and getting everything, you know, observe, orient, decide, act, is still so important today now with agents. I don't think anyone would have thought that we'd think about agents, but it really is. That longer-running agent piece, too, is so important because it frees up the warfighter or the executive to be strategic, which is really the important piece. The agents are doing the tactical work. That really is the one plus one equals three math that we're looking for. It's not just additive. That is a stepwise change in how we operate.

Daniel Buchmueller: Yeah, this is huge. I think the vision of every warfighter having access to an agent is not a strange vision, I believe. I think it's going to take some time for this to happen, but we need to be part of this revolution because there's a revolution in the commercial world happening very, very quickly. In my opinion, in our opinion, there's no reason why the warfighter should be left in the dust again when it comes to that. That's what really drives us: to build as equivalent as possible solutions for our warfighters.

Chad Walker: Yeah, that's awesome. Well, Daniel, I appreciate the time today. This is awesome. I hope people can understand and appreciate the hard work you're doing here. Thanks for joining me.

Daniel Buchmueller: Yeah, you bet. Thank you so much for having me.

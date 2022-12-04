import pytest
from sentinel.sentim import send_request


@pytest.mark.parametrize(
    ["text", "expected_sentiment"],
    [
        (
            "Random words in front of other random words create a random sentence.",
            "negative",
        ),
        (
            "This is the last random sentence I will be writing and I am going to stop mid-sent",
            "negative",
        ),
        (
            "For oil spots on the floor, nothing beats parking a motorbike in the lounge.",
            "neutral",
        ),
        ("I'm not a party animal, but I do like animal parties.", "neutral"),
        (
            "My dentist tells me that chewing bricks is very bad for your teeth.",
            "negative",
        ),
        (
            'Jason lived his life by the motto, "Anything worth doing is worth doing poorly."',
            "positive",
        ),
        (
            "The anaconda was the greatest criminal mastermind in this part of the neighborhood.",
            "positive",
        ),
        (
            "The opportunity of a lifetime passed before him as he tried to decide between a cone or a cup.",
            "neutral",
        ),
        (
            "He was the only member of the club who didn't like plum pudding.",
            "neutral",
        ),
        (
            "She found it strange that people use their cellphones to actually talk to one another.",
            "negative",
        ),
        (
            "A quiet house is nice until you are ordered to stay in it for months.",
            "positive",
        ),
        (
            "Hang on, my kittens are scratching at the bathtub and they'll upset by the lack of biscuits.",
            "neutral",
        ),
        ("Her life in the confines of the house became her new normal.", "positive"),
        (
            "The old rusted farm equipment surrounded the house predicting its demise.",
            "positive",
        ),
        ("This book is sure to liquefy your brain.", "positive"),
        ("All you need to do is pick up the pen and begin.", "neutral"),
        (
            "I am happy to take your donation; any amount will be greatly appreciated.",
            "positive",
        ),
        ("Andy loved to sleep on a bed of nails.", "positive"),
        ("This made him feel like an old-style rootbeer float smells.", "neutral"),
        (
            "The newly planted trees were held up by wooden frames in hopes they could survive the next storm.",
            "positive",
        ),
        (
            "He went back to the video to see what had been recorded and was shocked at what he saw.",
            "negative",
        ),
        ("The bread dough reminded her of Santa Clause's belly.", "neutral"),
        (
            "He learned the hardest lesson of his life and had the scars, both physical and mental, to prove it.",
            "negative",
        ),
        (
            "After fighting off the alligator, Brian still had to face the anaconda.",
            "neutral",
        ),
        (
            "One small action would change her life, but whether it would be for better or for worse was yet to be determined.",
            "negative",
        ),
        (
            "He had a hidden stash underneath the floorboards in the back room of the house.",
            "negative",
        ),
        ("You bite up because of your lower jaw.", "neutral"),
        (
            "His son quipped that power bars were nothing more than adult candy bars.",
            "positive",
        ),
        ("The river stole the gods.", "neutral"),
        ("He is no James Bond; his name is Roger Moore.", "neutral"),
        ("Beach-combing replaced wine tasting as his new obsession.", "positive"),
        (
            "The small white buoys marked the location of hundreds of crab pots.",
            "negative",
        ),
        ("The door slammed on the watermelon.", "neutral"),
        (
            "I honestly find her about as intimidating as a basket of kittens.",
            "positive",
        ),
        ("The underground bunker was filled with chips and candy.", "positive"),
        (
            "Writing a list of random sentences is harder than I initially thought it would be.",
            "negative",
        ),
        (
            "When she didn't like a guy who was trying to pick her up, she started using sign language.",
            "neutral",
        ),
        (
            "When nobody is around, the trees gossip about the people who have walked under them.",
            "neutral",
        ),
        ("I'm working on a sweet potato farm.", "positive"),
        ("Hit me with your pet shark!", "neutral"),
        (
            "The shark-infested South Pine channel was the only way in or out.",
            "neutral",
        ),
        ("Just because the water is red doesn't mean you can't drink it.", "negative"),
        (
            "Written warnings in instruction manuals are worthless since rabbits can't read.",
            "negative",
        ),
        ("He decided water-skiing on a frozen lake wasn't a good idea.", "positive"),
        (
            "Swim at your own risk was taken as a challenge for the group of Kansas City college students.",
            "positive",
        ),
        ("Baby wipes are made of chocolate stardust.", "neutral"),
        ("The quick brown fox jumps over the lazy dog.", "positive"),
        (
            "It's important to remember to be aware of rampaging grizzly bears.",
            "positive",
        ),
    ],
)
def test_send_request(text, expected_sentiment):
    response = send_request(text)
    assert response == expected_sentiment

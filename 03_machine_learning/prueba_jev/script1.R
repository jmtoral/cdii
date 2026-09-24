remotes::install_github("mountainMath/JevR")
install.packages("usethis")
usethis::edit_r_environ()

library(JevR)







questions <- list(
  urgent = jev_noul("Does this convey urgency?"),
  topic  = jev_choice("What is this message about?",
                      c(payments = "A payment or payout problem",
                        account  = "Logging in or account access",
                        other    = "Something else")),
  mood   = jev_score("How does the writer feel?",
                     c("Calm", "Frustrated", "Very angry"))
)

res <- jev("Help! My payouts have been failing for 3 days.", questions)
res
#> <jev_response> model: jev-1.13.0  tokens in/out: 350 / 30
#>   urgent (noul): p(yes) = 0.97
#>   topic (choice): payments  [confidence 0.95]
#>   mood (score): 1.10 of 0..2  [confidence 0.88]

jev_tidy(res)                    # one row: urgent, topic, topic_confidence, mood, ...
jev_probabilities(res, "mood")   # the full distribution over levels
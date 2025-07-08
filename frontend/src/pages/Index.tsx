
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { Cpu, ShoppingCart, Store, BarChart3, Rocket, Shield, Globe, Sparkles } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-100 to-purple-200">
      {/* Header */}
      <header className="container mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <motion.div
            className="flex items-center space-x-3"
            initial={{ y: -30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
              <Store className="w-7 h-7 text-white" />
            </div>
            <span className="text-3xl font-extrabold text-gray-800 tracking-wide">ADOGENT</span>
          </motion.div>
          
          <motion.nav
            className="hidden md:flex space-x-8"
            initial={{ y: -30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <a href="#features" className="text-gray-700 hover:text-gray-900 transition-colors font-medium">Features</a>
            <a href="#marketplace" className="text-gray-700 hover:text-gray-900 transition-colors font-medium">Marketplace</a>
            <a href="#about" className="text-gray-700 hover:text-gray-900 transition-colors font-medium">About</a>
          </motion.nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            className="space-y-8 max-w-2xl"
            initial={{ x: -60, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8 }}
          >
            <div className="space-y-6">
              <motion.div
                className="inline-flex items-center px-4 py-2 bg-blue-500/20 rounded-full border border-blue-400/30"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 }}
              >
                <Sparkles className="w-4 h-4 text-blue-600 mr-2" />
                <span className="text-blue-700 text-sm font-medium">AI-Powered Luxury Commerce</span>
              </motion.div>

              <h1 className="text-5xl lg:text-7xl font-extrabold leading-tight">
                <span className="text-gray-800">
                  Global Luxury
                </span>
                <br />
                <span className="text-3xl lg:text-5xl text-blue-600 font-semibold">
                  Zero Guesswork
                </span>
              </h1>

              <p className="text-xl text-gray-700 leading-relaxed max-w-lg">
                Our AI-powered agents scour trusted sources globally, delivering the best luxury deals in seconds. 
                Experience authentic luxury commerce with zero uncertainty.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-center space-x-8 text-blue-600">
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <span className="font-semibold">Authenticate</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Globe className="w-5 h-5" />
                  <span className="font-semibold">Compare</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5" />
                  <span className="font-semibold">Acquire</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-4">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Link to="/marketplace">
                    <Button className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg flex items-center gap-3">
                      <ShoppingCart className="w-5 h-5" />
                      Explore Marketplace
                    </Button>
                  </Link>
                </motion.div>

                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Link to="/ai-assistant">
                    <Button variant="outline" className="border-2 border-blue-500 text-blue-700 hover:bg-blue-500 hover:text-white backdrop-blur-sm px-8 py-4 rounded-xl text-lg font-semibold flex items-center gap-3">
                      <Cpu className="w-5 h-5" />
                      AI Assistant
                    </Button>
                  </Link>
                </motion.div>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-3 gap-4 pt-8">
              {[ 
                { label: "Accuracy", value: "99.5%", color: "text-blue-600", bgColor: "from-blue-400/20 to-blue-500/20" },
                { label: "Global Reach", value: "24/7", color: "text-indigo-600", bgColor: "from-indigo-400/20 to-indigo-500/20" },
                { label: "Deals Secured", value: "1000+", color: "text-purple-600", bgColor: "from-purple-400/20 to-purple-500/20" },
              ].map((item, i) => (
                <motion.div 
                  key={i}
                  whileInView={{ opacity: 1, y: 0 }} 
                  initial={{ opacity: 0, y: 20 }} 
                  transition={{ delay: i * 0.2 }}
                >
                  <Card className={`bg-gradient-to-br ${item.bgColor} backdrop-blur-xl border border-white/30 hover:border-blue-300/50 transition-all duration-300 rounded-xl`}>
                    <CardContent className="p-4 text-center">
                      <div className={`text-2xl lg:text-3xl font-extrabold ${item.color} mb-1`}>{item.value}</div>
                      <div className="text-gray-600 text-xs uppercase tracking-wider font-medium">{item.label}</div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            className="relative"
            initial={{ x: 60, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="space-y-6">
              {[ 
                { 
                  Icon: Cpu, 
                  title: "AI-Powered Analysis", 
                  desc: "Advanced algorithms analyze market trends and authenticate luxury items with 99.5% accuracy",
                  gradient: "from-blue-400/20 to-purple-400/20",
                  iconBg: "from-blue-500 to-purple-500"
                },
                { 
                  Icon: Shield, 
                  title: "Authenticated & Verified", 
                  desc: "Every item undergoes rigorous authentication by experts and AI verification systems",
                  gradient: "from-indigo-400/20 to-blue-400/20",
                  iconBg: "from-indigo-500 to-blue-500"
                },
                { 
                  Icon: BarChart3, 
                  title: "Market Intelligence", 
                  desc: "Real-time pricing data from global markets keeps you ahead of trends and opportunities",
                  gradient: "from-purple-400/20 to-indigo-400/20",
                  iconBg: "from-purple-500 to-indigo-500"
                }
              ].map((card, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.15 }}
                  whileHover={{ scale: 1.02, rotateY: 2 }}
                  className={`transform transition-all duration-300 ${index === 1 ? 'ml-8' : index === 2 ? 'mr-8' : ''}`}
                >
                  <Card className={`bg-gradient-to-br ${card.gradient} backdrop-blur-xl border border-white/30 hover:border-blue-300/50 transition-all duration-300 rounded-2xl shadow-xl`}>
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        <div className={`w-14 h-14 bg-gradient-to-r ${card.iconBg} rounded-xl flex items-center justify-center shadow-lg flex-shrink-0`}>
                          <card.Icon className="w-7 h-7 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-gray-800 font-bold text-lg mb-2">{card.title}</h3>
                          <p className="text-gray-700 text-sm leading-relaxed">{card.desc}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <motion.section
        id="features"
        className="container mx-auto px-6 py-20"
        initial={{ opacity: 0, y: 60 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="text-center mb-16 max-w-4xl mx-auto">
          <motion.div
            initial={{ scale: 0 }}
            whileInView={{ scale: 1 }}
            className="inline-flex items-center px-4 py-2 bg-blue-500/20 rounded-full border border-blue-400/30 mb-6"
          >
            <Sparkles className="w-4 h-4 text-blue-600 mr-2" />
            <span className="text-blue-700 text-sm font-medium">Why Choose ADOGENT</span>
          </motion.div>
          
          <h2 className="text-4xl lg:text-5xl font-extrabold text-gray-800 mb-6">
            The Future of Luxury Commerce
          </h2>
          <p className="text-gray-700 text-xl leading-relaxed">
            Experience autonomous luxury shopping with AI agents that work 24/7 to find, authenticate, and secure the best deals worldwide
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[ 
            {
              icon: <Cpu className="w-8 h-8" />,
              title: "Hunter Agents",
              description: "AI agents monitor 100+ platforms globally, finding underpriced luxury items while you sleep",
              color: "from-blue-500 to-indigo-500"
            },
            {
              icon: <Shield className="w-8 h-8" />,
              title: "Authentication AI",
              description: "99.5% accuracy in detecting fakes using advanced computer vision and expert verification",
              color: "from-indigo-500 to-purple-500"
            },
            {
              icon: <BarChart3 className="w-8 h-8" />,
              title: "Portfolio Manager",
              description: "Optimize your luxury collection for maximum appreciation with AI-driven insights",
              color: "from-purple-500 to-blue-500"
            },
            {
              icon: <Rocket className="w-8 h-8" />,
              title: "Concierge Service",
              description: "End-to-end luxury lifecycle management from purchase to authentication to resale",
              color: "from-blue-500 to-indigo-500"
            }
          ].map((feature, index) => (
            <motion.div 
              key={index} 
              whileInView={{ opacity: 1, y: 0 }} 
              initial={{ opacity: 0, y: 30 }} 
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, rotateY: 5 }}
            >
              <Card className="bg-white/60 backdrop-blur-xl border border-white/40 hover:border-blue-300/50 hover:bg-white/80 transition-all duration-300 group rounded-2xl shadow-xl h-full">
                <CardContent className="p-8 text-center h-full flex flex-col">
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-xl`}>
                    <div className="text-white">
                      {feature.icon}
                    </div>
                  </div>
                  <h3 className="text-gray-800 font-bold text-xl mb-4">{feature.title}</h3>
                  <p className="text-gray-700 text-sm leading-relaxed flex-1">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        className="container mx-auto px-6 py-20"
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
      >
        <Card className="bg-gradient-to-r from-blue-400/20 to-purple-400/20 backdrop-blur-xl border border-white/30 p-12 lg:p-16 text-center rounded-3xl shadow-2xl max-w-4xl mx-auto relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-3xl"></div>
          <CardContent className="p-0 relative z-10">
            <motion.div
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              className="inline-flex items-center px-4 py-2 bg-blue-500/30 rounded-full border border-blue-400/40 mb-8"
            >
              <Sparkles className="w-4 h-4 text-blue-700 mr-2" />
              <span className="text-blue-800 text-sm font-medium">Start Your Luxury Journey</span>
            </motion.div>

            <h2 className="text-3xl lg:text-4xl font-extrabold text-gray-800 mb-6">
              Ready to Transform Your Luxury Experience?
            </h2>
            <p className="text-gray-700 mb-10 max-w-2xl mx-auto text-lg leading-relaxed">
              Join thousands of luxury enthusiasts who trust ADOGENT's AI agents to find, authenticate, and manage their luxury collections
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link to="/marketplace">
                  <Button className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white px-12 py-4 rounded-xl text-lg font-semibold shadow-xl">
                    Start Shopping Now
                  </Button>
                </Link>
              </motion.div>

              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link to="/ai-assistant">
                  <Button variant="outline" className="border-2 border-blue-500 text-blue-700 hover:bg-blue-500 hover:text-white backdrop-blur-sm px-12 py-4 rounded-xl text-lg font-semibold">
                    Meet Your AI Assistant
                  </Button>
                </Link>
              </motion.div>
            </div>
          </CardContent>
        </Card>
      </motion.section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-12 border-t border-blue-300/50">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
              <Store className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-800">ADOGENT</span>
          </div>
          <p className="text-gray-600 text-sm">
            © 2025 Adogent. Revolutionizing luxury commerce with AI.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
